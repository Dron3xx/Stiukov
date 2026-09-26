import webbrowser as wb
from app.voice.speak import speak

def web_command(website):
    name = website["Name"]
    url = website["URL"]
    if not url:
        speak("Theres no link to it")
        return False
    else:
        wb.open(url)
        speak("Opening " + name)
        return True