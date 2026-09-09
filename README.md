# Stiukov

Stiukov is a Windows voice assistant written in Python. It focuses on voice interaction, desktop automation, and hands-on Python development.

The assistant can recognize wake words, respond to greetings and jokes, launch and close configured applications, open YouTube, and control system volume. The repository also includes `apps_search.py`, a separate exploratory script for finding executable files and reading Windows file metadata.

> Note: "Stiukov" is the project name and may be flagged by spell-checkers as a proper noun.

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
- Registry-based application path inspection
- Executable discovery in configured disk folders

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

To run the separate executable search script:

```powershell
python apps_search.py
```

`apps_search.py` checks the Windows App Paths registry and searches the folders configured in its `search_disk()` function. Those folders currently use example `D:` drive paths, so update them for the local machine before relying on the results.

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
- Say `search applications` to inspect application paths registered for the current Windows user
- Say `volume up`, `volume down`, `mute`, or `unmute`

Greetings and jokes are stored in `things/greetings.json` and `things/jokes.json`. Recognized words are appended to `saved_words.txt`.

The `search applications` command currently prints registry entries and whether their paths exist; it does not update `things/applications.json` or launch an application. `apps_search.py` is more extensive, but it is also exploratory: it searches fixed folders and prints executable metadata rather than creating a reusable application catalog.

## Project Structure

- `Stiukov.py` - main voice-assistant loop and command handlers
- `apps_search.py` - standalone Windows registry and disk executable search
- `things/applications.json` - application names, executable process names, and launch paths
- `things/greetings.json` - greeting phrases and responses
- `things/jokes.json` - joke questions and answers
- `saved_words.txt` - appended record of recognized command words
- `stiukov_explained.md` - detailed implementation walkthrough

## Troubleshooting

- Check that Windows has the correct default microphone selected.
- Allow Python to access the microphone in Windows privacy settings.
- `pycaw` volume control works with Windows audio devices.
- If an application does not open, check its path in `things/applications.json`.
- `calculator`, `opera`, and `edge` currently contain `YOUR_PATH_HERE` placeholders and must be configured before use.
- `apps_search.py` uses Windows-only APIs and may report no results when its configured folders do not exist.
