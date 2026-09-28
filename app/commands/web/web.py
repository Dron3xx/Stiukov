"""Open a known website using the browser."""

import webbrowser as wb

from app.voice.speak import speak


def web_command(website: dict[str, str | None]) -> bool:
    """Open the configured URL for a website record."""
    name = website["Name"]
    url = website["URL"]
    if not url:
        speak("Theres no link to it")
        return False
    wb.open(url)
    speak("Opening " + name)
    return True
