# Stiukov

## Overview

Stiukov is a Windows-focused Python voice assistant. It continuously listens through the default microphone and uses Google Speech Recognition to interpret spoken commands. The assistant can respond to greetings and jokes, open and close configured applications, search Windows for game and launcher entries, open YouTube, and control the system volume.

The assistant uses a local application state: it remains inactive until a configured wake word is detected and remains active until the `go to sleep` command is received.

## Technologies Used

- Python
- Windows
- SpeechRecognition
- pyttsx3
- psutil
- pycaw

## Requirements

- Windows 10 or 11
- Python 3.10 or newer
- A working microphone
- Internet access for Google Speech Recognition
- Dependencies from `requirements.txt`

## Installation

Clone the repository and install the Python dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Running the Assistant

From the project root:

```powershell
python -m app.main
```

The assistant can also be started directly:

```powershell
python app\main.py
```

After starting, the assistant continuously listens through the default microphone.

The assistant initially waits for a configured wake word. After activation, recognized speech is passed to the command handlers until `go to sleep` is received.

## Current Command Patterns

The current implementation supports:

- configured wake-word variations to activate the assistant
- greeting phrases loaded from `things/greetings.json`
- jokes containing the word `joke`
- `open <application>` to launch an application from the generated catalog
- `close <application>` to terminate a matching running process
- `search applications` to rebuild the local application catalog
- `open youtube`
- `volume up`
- `volume down`
- `mute`
- `unmute`
- `go to sleep` to deactivate the assistant

## Application Discovery

Stiukov can generate an application catalog from the local Windows environment.

The discovery process checks:

- Windows Registry protocol handlers
- Start Menu `.lnk` shortcuts
- Windows AppX launcher information through PowerShell `Get-StartApps`

The search is focused on game and launcher-related entries using configured keywords such as:

- `games`
- `gry`
- `steam`
- `epic`
- `battle.net`
- `origin`
- `gog`
- `ubisoft`
- `uplay`
- `riot`
- `launcher`
- `xbox`
- `minecraft`

The resulting catalog is stored in `things/applications.json`.

If the catalog does not exist when the application starts, Stiukov generates it automatically. The catalog can also be regenerated with:

```text
search applications
```

## Repository Structure

```text
Stiukov/
├── app/
│   ├── __init__.py
│   ├── apps_search.py
│   └── main.py
├── commands/
├── memory/
├── tests/
├── things/
│   ├── greetings.json
│   └── jokes.json
├── Dockerfile
├── README.md
├── explained.md
├── requirements.txt
├── requirements-dev.txt
├── run_tests.py
├── saved_words.txt
├── voice/
└── .gitignore
```

`things/applications.json` is generated at runtime when the application catalog does not exist and is not part of the checked-in repository structure.

## Notes

- The project is Windows-specific because it uses Windows APIs and components such as `winreg`, `os.startfile`, Windows audio APIs, and PowerShell.
- Speech recognition uses Google Speech Recognition and therefore requires an internet connection.
- Application discovery focuses on game and launcher-related entries rather than every installed application.
- Recognized command words are appended to `saved_words.txt` during runtime.
- Application launching and closing depend on the generated application catalog and Windows process information.
