"""Handle system volume commands."""

from app.commands.system.volume import volume_command
from app.memory.system.volume.volume import load_volume


def volume_handler(voice_data: str) -> bool:
    """Apply a recognized volume action if the command is present."""
    volume = load_volume()
    for command, function in volume.items():
        if command in voice_data:
            return volume_command(function)

    return False
