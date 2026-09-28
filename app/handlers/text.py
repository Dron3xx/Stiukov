from app.commands.system.text import text_operations
from app.memory.system.text.text import save_text

def text_handler(voice_data):

    if "save" in voice_data:
        return text_operations(voice_data, save_text)

    return False