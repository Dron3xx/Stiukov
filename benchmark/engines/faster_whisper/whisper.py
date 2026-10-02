from faster_whisper import WhisperModel
import atexit
import sys
import time
from pathlib import Path
from mutagen.mp4 import MP4

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


log_file = (Path(__file__).resolve().parent / "whisper.log").open(
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
    "tiny",
    "small",
    "large",
]

DEVICES = [
    "cpu",
    "cuda",
]

def benchmark_model(model_name, model, device, path: Path) -> dict:

    start = time.time()
    segments, info = model.transcribe(str(path), language="en")
    audio_duration = MP4(path).info.length

    full_text = " ".join(segment.text for segment in segments)
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
        if device == "cpu":
            model = WhisperModel(model_name, device=device, compute_type="int8")
        else:
            model = WhisperModel(model_name, device=device, compute_type="float16")
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