import pyautogui
import pyperclip
import time
import re
from app.voice.speak import speak
from app.voice.record_audio import record_audio

def text_operations(voice_data, save_text):
    cleaned = re.sub(r"^save ", " ", voice_data)

    text_to_save = ""
    if cleaned != voice_data:
        text_to_save = cleaned.strip(" ")
    else:
        before = pyperclip.paste()

        pyautogui.hotkey("ctrl", "c")
        time.sleep(0.2)

        after = pyperclip.paste()

        if after != before:
            speak("Text is pasted")
            text_to_save = after
        else:
            speak("What do you want to save?")
            text_to_save = record_audio()

    return save_text(text_to_save)