"""Handle text-saving commands."""

import re
import time
from collections.abc import Callable

import pyautogui
import pyperclip

from app.voice.record_audio import record_audio
from app.voice.speak import speak


def text_operations(voice_data: str, save_text: Callable[[str], bool]) -> bool:
    """Save clipboard text or a spoken phrase requested by the user."""
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
