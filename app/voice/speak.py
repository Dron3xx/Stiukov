"""Speak text aloud using the system TTS engine."""

import pyttsx3


def speak(text: str) -> None:
    """Convert text to speech and print it to the console."""
    engine = pyttsx3.init()
    engine.setProperty("rate", 175)
    engine.setProperty("volume", 1)

    print(f"Stiukov: {text}")

    engine.say(text)
    engine.runAndWait()
    engine.stop()
