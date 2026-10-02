import json
import atexit
import sys
import time
from pathlib import Path

import av
from mutagen.mp4 import MP4
from vosk import GpuInit, GpuThreadInit, KaldiRecognizer, Model

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


log_file = (Path(__file__).resolve().parent / "vosk.log").open(
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
    "Small",
    "Medium-ish",
    "Large",
]

VOSK_MODELS = {
    "Small": "vosk-model-small-en-us-0.15",
    "Medium-ish": "vosk-model-en-us-0.22-lgraph",
    "Large": "vosk-model-en-us-0.22",
}

DEVICES = [
    "cuda",
]

if "cuda" in DEVICES:
    GpuInit()

def benchmark_model(model_name, model, device, path: Path) -> dict:

    start = time.time()
    recognizer = KaldiRecognizer(model, 16000)
    text_segments = []

    with av.open(str(path)) as container:
        audio_stream = next(stream for stream in container.streams if stream.type == "audio")
        resampler = av.AudioResampler(format="s16", layout="mono", rate=16000)

        for frame in container.decode(audio_stream):
            for resampled_frame in resampler.resample(frame):
                audio_data = resampled_frame.to_ndarray().tobytes()
                if recognizer.AcceptWaveform(audio_data):
                    text_segments.append(json.loads(recognizer.Result()).get("text", ""))

        for resampled_frame in resampler.resample(None):
            audio_data = resampled_frame.to_ndarray().tobytes()
            if recognizer.AcceptWaveform(audio_data):
                text_segments.append(json.loads(recognizer.Result()).get("text", ""))

        final_result = json.loads(recognizer.FinalResult())
        text_segments.append(final_result.get("text", ""))

    audio_duration = MP4(path).info.length

    full_text = " ".join(text for text in text_segments if text)
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
        if device == "cuda":
            GpuThreadInit()
            model = Model(model_name=VOSK_MODELS[model_name])
        else:
            model = Model(model_name=VOSK_MODELS[model_name])
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