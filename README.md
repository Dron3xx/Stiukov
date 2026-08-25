# Stiukov

Stiukov is a Windows voice assistant written in Python. It is a personal project focused on voice interaction, desktop automation, and learning Python through practical development.

The assistant can recognize wake words, respond to greetings and jokes, launch and close applications, open YouTube, and control system volume.

## Features

- Wake-word detection
- Voice command recognition
- Active and sleep modes
- Text-to-speech responses
- Configurable greetings and jokes
- Application launching
- Application process management
- YouTube launching
- System volume control
- Mute / unmute
- JSON-based application configuration

## Requirements

- Windows
- Python 3.10 or newer
- A working microphone
- An internet connection for speech recognition
- The required Python packages are listed in `requirements.txt`

## Installation

Clone the repository and open PowerShell in the project folder.

Install the required Python packages:

```powershell
python -m pip install -r requirements.txt
```

If `python` is not recognized, install Python from [python.org](https://www.python.org/downloads/) and enable **Add Python to PATH** during installation.

## Run

```powershell
python Stiukov.py
```

The assistant listens through the default microphone. Speech recognition uses Google's online speech-recognition service, so an internet connection is required.

## Wake Words

Say one of the recognized wake words before a command, for example:

```text
speaker open youtube
```

The assistant remains active until you say:

```text
go to sleep
```

## Commands

- Say a greeting, such as `hello`
- Say `tell me a joke`
- Say `open youtube`
- Say `open <application>` or `close <application>` for an application configured in `things/applications.json`
- Say `volume up`, `volume down`, `mute`, or `unmute`

Greetings and jokes are stored in `things/greetings.json` and `things/jokes.json`. Recognized words are appended to `saved_words.txt`.

## Troubleshooting

- Check that Windows has the correct default microphone selected.
- Allow Python to access the microphone in Windows privacy settings.
- `pycaw` volume control works with Windows audio devices.
- If an application does not open, check its path in `things/applications.json`.
