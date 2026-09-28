from app.voice.speak import speak


def greeting_command(response):

    speak(response)

    return True