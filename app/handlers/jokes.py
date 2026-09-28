"""Handle joke-related voice commands."""

from app.commands.jokes.joke import joke_command
from app.memory.jokes.jokes import load_jokes


def jokes_handler(voice_data: str) -> bool:
    """Trigger a joke when the user asks for one."""
    if "joke" in voice_data:
        jokes = load_jokes()
        return joke_command(jokes)

    return False
