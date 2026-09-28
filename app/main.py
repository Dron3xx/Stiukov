# =========================
# SYSTEM
# =========================
import os
import sys
import time
import threading
import subprocess
import json
from pathlib import Path

# =========================
# LOCAL MODULES
# =========================
from app.handlers.application import (
    applications_handler, 
    ensure_applications_file
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
    wake_word_detector
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

project_dir = Path(__file__).parent.parent

things_directory = project_dir / "things"

applications_file_path = things_directory / "applications.json"


def save_words_to_file(words):
    saved_words_file_path = os.path.join(project_dir, "saved_words.txt")
    with open(saved_words_file_path, "a", encoding="utf-8") as file:
        file.write(" ".join(words) + "\n")


def respond(voice_data):

    if not is_active():
        print("assistant isn't active")
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

        except Exception as error:
            print(f"The assistant recovered from an error: {error}")
