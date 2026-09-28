"""Handle greeting-related voice commands."""

from app.commands.greetings.greeting import greeting_command
from app.memory.greetings.greetings import load_greetings


def greetings_handler(voice_data: str) -> bool:
    """Return the greeting response when a configured greeting is found."""
    greetings = load_greetings()
    for greeting, response in greetings.items():
        if greeting in voice_data:
            return greeting_command(response)

    return False
