import shutil
import atexit
import sys
import time
from pathlib import Path
from urllib.request import urlretrieve

import av
from mutagen.mp4 import MP4
import numpy as np
import sherpa_onnx

class OutputTee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, text):
        for stream in self.streams:
            stream.write(text)
        return len(text)

    def flush(self):
        for stream in self.streams:
            stream.flush()


log_file = (Path(__file__).resolve().parent / "sherpa.log").open(
    "w", encoding="utf-8", buffering=1
)
sys.stdout = OutputTee(sys.stdout, log_file)
atexit.register(log_file.close)

recordings_path = Path(__file__).resolve().parents[2] / "recordings"

audio_extensions = {".wav", ".mp3", ".m4a", ".flac", ".ogg"}

audio_files = [
    p for p in recordings_path.rglob("*")
    if p.is_file() and p.suffix.lower() in audio_extensions
]

print(f"files found: {len(audio_files)}")
for p in audio_files:
    print(p)

MODELS = [
    "small",
    "medium",
    "large",
]

MODEL_DIRECTORIES = {
    "small": "sherpa-onnx-zipformer-small-en-2023-06-26",
    "medium": "sherpa-onnx-zipformer-en-2023-06-26",
    "large": "sherpa-onnx-zipformer-large-en-2023-06-26",
}

DEVICES = [
    "cpu",
]

def load_model(model_name: str, device: str):
    model_directory = MODEL_DIRECTORIES[model_name]
    models_path = Path(__file__).resolve().parents[2] / "models"
    model_path = models_path / model_directory
    encoder_path = model_path / "encoder-epoch-99-avg-1.int8.onnx"
    decoder_path = model_path / "decoder-epoch-99-avg-1.onnx"
    joiner_path = model_path / "joiner-epoch-99-avg-1.int8.onnx"
    tokens_path = model_path / "tokens.txt"

    if not all(path.exists() for path in (encoder_path, decoder_path, joiner_path, tokens_path)):
        models_path.mkdir(parents=True, exist_ok=True)
        archive_path = models_path / f"{model_directory}.tar.bz2"
        model_url = (
            "https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/"
            f"{model_directory}.tar.bz2"
        )
        urlretrieve(model_url, archive_path)
        shutil.unpack_archive(str(archive_path), str(models_path))
        archive_path.unlink()

    return sherpa_onnx.OfflineRecognizer.from_transducer(
        encoder=str(encoder_path),
        decoder=str(decoder_path),
        joiner=str(joiner_path),
        tokens=str(tokens_path),
        num_threads=2,
        provider=device,
    )


def benchmark_model(model_name, model, device, path: Path) -> dict:

    start = time.time()
    stream = model.create_stream()

    with av.open(str(path)) as container:
        audio_stream = next(stream for stream in container.streams if stream.type == "audio")
        resampler = av.AudioResampler(format="fltp", layout="mono", rate=16000)

        for frame in container.decode(audio_stream):
            for resampled_frame in resampler.resample(frame):
                waveform = np.asarray(resampled_frame.to_ndarray()).reshape(-1)
                stream.accept_waveform(16000, waveform)

        for resampled_frame in resampler.resample(None):
            waveform = np.asarray(resampled_frame.to_ndarray()).reshape(-1)
            stream.accept_waveform(16000, waveform)

    model.decode_stream(stream)
    full_text = stream.result.text
    audio_duration = MP4(path).info.length

    elapsed = time.time() - start

    return {
        "model": model_name,
        "device": device,
        "audio": str(path),
        "text": full_text,
        "elapsed_seconds": round(elapsed, 3),
        "audio_duration": round(audio_duration, 3),
        "RTF": round(elapsed / audio_duration, 3),
    }


for model_name in MODELS:
    for device in DEVICES:
        model = load_model(model_name, device)
        for audio_file in audio_files:
            result = benchmark_model(model_name, model, device, audio_file)
            print(f"Model: {result['model']}")
            print(f"Device: {result['device']}")
            print(f"Audio: {result['audio']}")
            print(f"Text: {result['text']}")
            print(f"Elapsed: {result['elapsed_seconds']}")
            print(f"Audio duration: {result['audio_duration']}")
            print(f"RTF: {result['RTF']}")
            print("-------------------")