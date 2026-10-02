"""Manage the assistant wake-word activation state."""

import re


def is_stiukov(voice_data: str) -> str | None:
    """Return the detected wake word if the user is addressing the assistant."""
    # Include common speech-recognition variations of the assistant name.
    wake_words = [
        "stukov",
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
        "sick off",
        "stick-off",
        "sikov",
    ]

    for word in wake_words:
        pattern = rf"\b{re.escape(word)}\b"

        if re.search(pattern, voice_data):
            print(f"Wake word detected: {word}")
            return word

    return None


assistant_active = False


def is_active() -> bool:
    """Return whether the assistant is currently active."""
    return assistant_active


def activate() -> bool:
    """Enable the assistant so it can respond to commands."""
    global assistant_active
    assistant_active = True

    return assistant_active


def deactivate() -> bool:
    """Disable the assistant and stop processing commands."""
    global assistant_active
    assistant_active = False

    return assistant_active


def wake_word_detector(voice_data: str) -> str:
    """Activate the assistant and strip the wake-word phrase from the command."""
    wake_word = is_stiukov(voice_data)

    if wake_word:
        activate()
        voice_data = re.sub(
            rf"\b{re.escape(wake_word)}\b",
            "",
            voice_data,
        ).strip()

    return voice_data
