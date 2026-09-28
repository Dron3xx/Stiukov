"""Respond to a greeting request."""

from app.voice.speak import speak


def greeting_command(response: str) -> bool:
    """Speak the configured greeting response."""
    speak(response)

    return True
