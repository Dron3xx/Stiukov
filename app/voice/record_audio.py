"""Capture microphone audio and transcribe detected speech."""
import os
import queue

import numpy as np

STIUKOV_TESTING = os.environ.get("STIUKOV_TESTING") == "1"

if not STIUKOV_TESTING:
    import silero_vad
    import sounddevice as sd
    from faster_whisper import WhisperModel

    sd.default.samplerate = 16000
    sd.default.channels = 1

VAD_FRAME_SIZE=512
PRE_AUDIO_BUFFER_LIMIT=4


class AudioCapture:
    """Manage microphone capture and speech transcription."""

    def __init__(self) -> None:
        """Initialize the transcription model, input stream, and VAD."""
        self.model = WhisperModel("large", device="cuda", compute_type="float16")

        self.audio_queue = queue.Queue()

        self.stream = sd.InputStream(
            callback=self.audio_callback,
            channels=1,
            samplerate=16000,
        )
        self.stream.start()

        self.vad_model = silero_vad.load_silero_vad()
        self.vad_iterator = silero_vad.VADIterator(
                self.vad_model,
                min_silence_duration_ms = 500,
                speech_pad_ms = 100,
        )

        self.frame_buffer = np.array([], dtype=np.float32)

    def audio_callback(
        self,
        indata: np.ndarray,
        frames: int,
        time: object,
        status: object,
    ) -> None:
        """Capture audio data from the microphone."""
        self.audio_queue.put(indata)


    def record_audio(
        self,
        ask: str | None = None) -> str:
        """Listen for speech and return the recognized text in lower case."""
        audio_buffer = []
        pre_audio_buffer = []
        is_speech = False
        if ask:
            print(ask)
        print("Listening...")
        while True:

            chunk = self.audio_queue.get()
            self.frame_buffer = np.concatenate((self.frame_buffer, chunk.reshape(-1)))
            if self.frame_buffer.shape[0] >= VAD_FRAME_SIZE:
                frame = self.frame_buffer[:VAD_FRAME_SIZE]
                self.frame_buffer = self.frame_buffer[VAD_FRAME_SIZE:]
                vad_result = self.vad_iterator(frame)
                pre_audio_buffer.append(frame)
                if len(pre_audio_buffer) > PRE_AUDIO_BUFFER_LIMIT:
                    pre_audio_buffer = pre_audio_buffer[1:]
                if vad_result:
                    if "start" in vad_result:
                        pre_audio_buffer = pre_audio_buffer[:-1]
                        audio_buffer.extend(pre_audio_buffer)
                        is_speech = True

                    if "end" in vad_result:
                        full_audio = np.concatenate(audio_buffer)
                        audio_buffer = []
                        print("Recognizing...")
                        segments, info = self.model.transcribe(full_audio, language="en")
                        voice_data = " ".join(segment.text for segment in segments)
                        print(len(full_audio))
                        print(f"Recognized: {voice_data.lower()}")
                        is_speech = False
                        return voice_data.lower()

                if is_speech:
                    audio_buffer.append(frame)


if not STIUKOV_TESTING:
    audio_capture = AudioCapture()


def record_audio(ask: str | None = None) -> str:
    """Capture speech and return its transcription in lowercase."""
    return audio_capture.record_audio(ask)
