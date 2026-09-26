from app.commands.web.web import web_command
from app.memory.web.website import load_websites

def web_handler(voice_data):
    websites = load_websites()

    for website in websites:
        if "open "+ website.lower() in voice_data:
            return web_command(websites[website])

    return False