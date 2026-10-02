"""Capture and transcribe spoken input from the microphone."""

from faster_whisper import WhisperModel
import queue
import numpy as np
import sounddevice as sd
import silero_vad


model = WhisperModel("large", device="cuda", compute_type="float16")

sd.default.samplerate = 16000
sd.default.channels = 1
audio_queue = queue.Queue()


def audio_callback(indata, frames, time, status):
    """Callback function to capture audio data from the microphone."""
    audio_queue.put(indata)


stream = sd.InputStream(callback=audio_callback, channels=1, samplerate=16000)
stream.start()

vad_model = silero_vad.load_silero_vad()
vad_iterator = silero_vad.VADIterator(vad_model)
frame_buffer = np.array([], dtype=np.float32)
audio_buffer = []
is_speech = False

while True:
    chunk = audio_queue.get()
    frame_buffer = np.concatenate((frame_buffer, chunk.reshape(-1)))
    if frame_buffer.shape[0] >= 512:
        frame = frame_buffer[:512]
        frame_buffer = frame_buffer[512:]
        vad_result = vad_iterator(frame)
        if vad_result:
            if "start" in vad_result:
                is_speech = True
            
            if "end" in vad_result:
                full_audio = np.concatenate(audio_buffer)
                audio_buffer = []
                segments, info = model.transcribe(full_audio, language="en")
                full_text = " ".join(segment.text for segment in segments)
                print(full_text)
                is_speech = False

        if is_speech:
            audio_buffer.append(frame)

