import re

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


def is_active():
    return assistant_active


def activate():
    global assistant_active
    assistant_active = True

    return assistant_active


def deactivate():
    global assistant_active
    assistant_active = False

    return assistant_active


def wake_word_detector(voice_data):
    wake_word = is_stiukov(voice_data)

    if wake_word:
        activate()
        voice_data = re.sub(
            rf"\b{re.escape(wake_word)}\b",
            "",
            voice_data
        ).strip()

    return voice_data