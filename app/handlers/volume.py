
from app.commands.system.volume import volume_command
from app.memory.system.volume.volume import load_volume


def volume_handler(voice_data):
    volume = load_volume()
    for command, function in volume.items():
        if command in voice_data:
            return volume_command(function)


    return False