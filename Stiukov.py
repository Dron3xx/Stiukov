# =========================
# SYSTEM
# =========================
import os
import sys
import time
import random
import threading
import subprocess
import json
import winreg
import win32api

# =========================
# VOICE
# =========================
import speech_recognition as sr
import pyttsx3
import re

# =========================
# COMPUTER CONTROL
# =========================
import keyboard
import pyautogui
import pyperclip
import psutil

# =========================
# WEB
# =========================
import webbrowser as wb

# =========================
# IMAGE / VISION
# =========================
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

# =========================
# AUDIO
# =========================
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume

# =========================
# AI / ML
# =========================
from tensorflow.keras.models import load_model

current_directory = os.path.dirname(os.path.abspath(__file__))

things_directory = os.path.join(current_directory, "things")

applications_file_path = os.path.join(things_directory, "applications.json")
greetings_file_path = os.path.join(things_directory, "greetings.json")
jokes_file_path = os.path.join(things_directory, "jokes.json")



def is_stiukov(voice_data):
    # Include common speech-recognition variations of the assistant name.
    wake_words = [
        "stuck off",
        "stucco",
        "stick off",
        "sticker",
        "sicko",
        "stickers",
        "tickle",
        "sick off",
        "stupid",
        "take off",
        "speaker",
        "sick off"
    ]

    for word in wake_words:
        pattern = rf"\b{re.escape(word)}\b"

        if re.search(pattern, voice_data):
            print(f"Wake word detected: {word}")
            return word

    return None

assistant_active = False

def wake_word_detector(voice_data):
    global assistant_active

    # Activate the assistant and remove the wake word before dispatching.
    wake_word = is_stiukov(voice_data)

    if wake_word:
        assistant_active = True

        voice_data = re.sub(
            rf"\b{re.escape(wake_word)}\b",
            "",
            voice_data
        ).strip()

    return voice_data


def speak(text):
    engine = pyttsx3.init()
    engine.setProperty("rate", 175)
    engine.setProperty("volume", 1)

    print(f"Stiukov: {text}")

    engine.say(text)
    engine.runAndWait()
    engine.stop()


def save_words_to_file(words):
    saved_words_file_path = os.path.join(current_directory, "saved_words.txt")
    with open(saved_words_file_path, "a", encoding="utf-8") as file:
        file.write(" ".join(words) + "\n")


recognizer = sr.Recognizer()

def record_audio(ask=False):
    voice_data = ''
    with sr.Microphone() as source:
        if ask:
            print(ask)
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            print("Recognizing...")
            voice_data = recognizer.recognize_google(audio, language='en-EN')
            print(f"Recognized: {voice_data}")
        except sr.UnknownValueError:
            print('Speech not recognized')
        except sr.RequestError as e:
            print(f'Could not request results; {e}')
    return voice_data.lower()


def respond(voice_data):
    global assistant_active

    if not assistant_active:
        print("assistant isn't active")
        return

    if voice_data:
        # Keep a simple history of recognized command words.
        words = voice_data.split()
        save_words_to_file(words)


    if "go to sleep" in voice_data:
        assistant_active = False
        speak("Going to sleep.")
        return

    if search_applications(voice_data):
        return

    if handle_greeting(voice_data):
        return

    if handle_joke(voice_data):
        return

    if handle_application(voice_data):
        return

    if handle_web_command(voice_data):
        return

    if handle_volume(voice_data):
        return

    speak("I can't help you with it yet")

def search_applications(voice_data):
    # Inspect application paths registered for the current Windows user.
    reg_path = r"Software\Microsoft\Windows\CurrentVersion\App Paths"
    if "search applications" in voice_data:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ) as parent_key:
            i = 0
            apps = {}
            while True:
                try:
                    sub_key = winreg.EnumKey(parent_key, i)
                    with winreg.OpenKey(parent_key, sub_key, 0, winreg.KEY_READ) as child_key:
                        try:
                            value, _ = winreg.QueryValueEx(child_key, "")
                            print("sub_key:", sub_key)
                            print("Value:", value)
                            print(os.path.exists(value))
                        except FileNotFoundError:
                            pass
                    i += 1
                except OSError:
                    break
        #winreg.QueryValueEx()

    return False


def handle_joke(voice_data):
    if "joke" in voice_data:
        joke = random.choice(list(jokes.values()))
        speak(f'{joke["question"]} {joke["answer"]}')
        return True

    return False

def handle_greeting(voice_data):
    for greeting, response in greetings.items():
        if greeting in voice_data:
            speak(response)
            return True

    return False

def handle_application(voice_data):
    for app_name in applications:
        # Normalize process names because Windows names are case-insensitive.
        process_name = applications[app_name]["process"].lower()
        if "close "+ app_name in voice_data:
            for process in psutil.process_iter(["name"]):
                try:
                    name = process.info["name"]

                    if name and name.lower() == process_name:
                        parent = process.parent()

                        if parent and parent.name().lower() != process_name:
                            process.terminate()
                            speak("Closing " + app_name)
                            return True

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            speak(app_name +" is not running")
            return True
        if "open "+ app_name in voice_data:
            os.startfile(applications[app_name]["path"])
            speak("Opening "+ app_name)
            return True

    return False

def handle_web_command(voice_data):
    if "open youtube" in voice_data:
        wb.open("https://www.youtube.com")
        speak("Opening YouTube.")
        return True

    return False

def handle_volume(voice_data):
    # Use the default Windows speaker endpoint for all volume commands.
    devices = AudioUtilities.GetSpeakers()
    volume = devices.EndpointVolume

    if "volume up" in voice_data:
        current_volume = volume.GetMasterVolumeLevelScalar()
        new_volume = min(current_volume + 0.1, 1.0)
        volume.SetMasterVolumeLevelScalar(new_volume, None)
        speak("Volume up")
        return True

    if "volume down" in voice_data:
        current_volume = volume.GetMasterVolumeLevelScalar()
        new_volume = max(current_volume - 0.1, 0.0)
        volume.SetMasterVolumeLevelScalar(new_volume, None)
        speak("Volume down")
        return True

    if "unmute" in voice_data:
        volume.SetMute(0, None)
        speak("Unmuting")
        return True

    if "mute" in voice_data:
        volume.SetMute(1, None)
        speak("Muting")
        return True

    return False

def load_greetings():
    # Keep response text in JSON so it can be edited without changing logic.
    with open(greetings_file_path, "r", encoding="utf-8") as file:
        greetings_data = json.load(file)
    return greetings_data["greetings"]

greetings = load_greetings()


def load_jokes():
    with open(jokes_file_path, "r", encoding="utf-8") as file:
        jokes_data = json.load(file)
    return jokes_data["jokes"]

jokes = load_jokes()


def load_applications():
    with open(applications_file_path, "r", encoding="utf-8") as file:
        applications_data = json.load(file)
    return applications_data["applications"]

applications = load_applications()

while True:
    try:
        # Listen continuously and recover from errors without exiting.
        voice_data = record_audio()

        if not voice_data:
            continue

        if not assistant_active:
            voice_data = wake_word_detector(voice_data)

            if not voice_data:
                continue

        respond(voice_data)

    except Exception as error:
        print(f"The assistant recovered from an error: {error}")
