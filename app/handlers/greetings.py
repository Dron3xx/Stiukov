from app.commands.greetings.greeting import greeting_command
from app.memory.greetings.greetings import load_greetings


def greetings_handler(voice_data):
    greetings = load_greetings()
    for greeting, response in greetings.items():
        if greeting in voice_data:
            return greeting_command(response)

    return False