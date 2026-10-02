"""Entry point for the voice assistant command loop."""

# =========================
# SYSTEM
# =========================
import os
import sys
import threading
import time
from pathlib import Path

# =========================
# LOCAL MODULES
# =========================
from app.handlers.applications import (
    applications_handler,
    ensure_applications_file,
)
from app.handlers.jokes import jokes_handler
from app.handlers.greetings import greetings_handler

# =========================
# VOICE
# =========================

from app.voice.speak import speak
from app.voice.record_audio import record_audio
from app.voice.activation.active import (
    is_active,
    deactivate,
    wake_word_detector,
)

# =========================
# COMPUTER CONTROL
# =========================
import keyboard
from app.handlers.text import text_handler
import psutil

# =========================
# WEB
# =========================
from app.handlers.web import web_handler

# =========================
# IMAGE / VISION
# =========================
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

# =========================
# AUDIO
# =========================
from app.handlers.volume import volume_handler

# =========================
# AI / ML
# =========================
from tensorflow.keras.models import load_model


if not os.environ.get("PYTEST_CURRENT_TEST"):
    ensure_applications_file()

project_dir = Path(__file__).parent[2]
things_dir = project_dir / "things"


def save_words_to_file(words: list[str]) -> None:
    """Append recent spoken command words to the saved words log."""
    saved_words_file_path = things_dir / "saved_words.txt"
    with saved_words_file_path.open("a", encoding="utf-8") as file:
        file.write(" ".join(words) + "\n")


def respond(voice_data: str) -> None:
    """Handle a recognized voice command and route it to the correct handler."""
    if not is_active():
        print("assistant isn't active")  # noqa: T201 - visible assistant status.
        return

    if voice_data:
        # Keep a simple history of recognized command words.
        words = voice_data.split()
        save_words_to_file(words)

    if "go to sleep" in voice_data:
        deactivate()
        speak("Going to sleep.")
        return

    if text_handler(voice_data):
        return

    if greetings_handler(voice_data):
        return

    if jokes_handler(voice_data):
        return

    if applications_handler(voice_data):
        return

    if web_handler(voice_data):
        return

    if volume_handler(voice_data):
        return

    speak("I can't help you with it yet")


if __name__ == "__main__":
    while True:
        try:
            # Listen continuously and recover from errors without exiting.
            voice_data = record_audio()

            if not voice_data:
                continue

            if not is_active():
                voice_data = wake_word_detector(voice_data)

                if not voice_data:
                    continue

            respond(voice_data)

        except Exception as error:  # noqa: BLE001 - keep the assistant loop alive during unexpected runtime failures.
            print(f"The assistant recovered from an error: {error}")  # noqa: T201 - visible recovery status.
