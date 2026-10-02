# Stiukov

## Overview

Stiukov is a Windows-focused Python voice assistant. It captures microphone audio with `sounddevice`, detects speech with Silero VAD, and transcribes English speech with `faster-whisper` using Whisper Large on CUDA with FP16. It can answer configured greetings and jokes, save text, open websites, discover and control selected Windows applications, and adjust system volume.

The assistant remains inactive until it detects a configured wake-word variation. It then processes commands until it receives `go to sleep`.

## Technologies Used

- Python
- Windows
- faster-whisper (Whisper Large, CUDA, FP16)
- sounddevice and Silero VAD
- pyttsx3
- NumPy
- pyautogui and pyperclip
- psutil
- pycaw

## Requirements

- Windows 10 or 11
- Python 3.11.x is used by CI; the Docker image uses Python 3.14.7
- A working microphone
- A CUDA-capable NVIDIA GPU and compatible CUDA runtime for the configured Whisper model
- Dependencies from `requirements.txt`

## Installation

Clone the repository and install the Python dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Running the Assistant

From the project root, run:

```powershell
python -m app.main
```

The application initializes the Windows application catalog when it is missing, then continuously listens through the default microphone. Speak a configured wake-word variation to activate command handling; say `go to sleep` to return to the inactive state.

## Current Command Patterns

The current implementation supports:

- configured wake-word variations to activate the assistant
- greeting phrases loaded from `app/memory/greetings/greetings.json`
- jokes containing the word `joke`
- `save <text>` to save spoken text, or `save` to save selected clipboard text (with spoken fallback)
- `open <website>` for a website configured in `app/memory/web/websites.json`
- `open <application>` and `close <application>` for entries in the generated application catalog
- `search applications` to rebuild that catalog
- `volume up`, `volume down`, `mute`, and `unmute`, as configured in `app/memory/system/volume/volume.json`
- `go to sleep` to deactivate the assistant

## Application Discovery

Stiukov can generate an application catalog from the local Windows environment.

The discovery process checks:

- Windows Registry protocol handlers
- Start Menu `.lnk` shortcuts
- Windows AppX launcher information through PowerShell `Get-StartApps` (currently filtered for Minecraft)

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

The catalog is stored at `app/memory/system/applications/applications.json`.

If the catalog does not exist when the application starts, Stiukov generates it automatically. It can also be regenerated with:

```text
search applications
```

## Repository Structure

```text
Stiukov/
├── app/
│   ├── main.py
│   ├── commands/       # Perform speech, text, web, volume, and app actions
│   ├── handlers/       # Route recognized text to commands and data
│   ├── memory/         # JSON-backed settings and saved data
│   └── voice/          # Audio capture, wake-word state, and speech output
├── tests/
│   ├── application/
│   └── documentation/
├── benchmark/
│   ├── engines/        # faster-whisper, sherpa-onnx, and Vosk experiments
│   └── recordings/     # Speech recordings organized by scenario
├── things/
│   └── saved_words.txt
├── Dockerfile
├── README.md
├── explained.md
├── pyproject.toml
├── pytest.ini
├── requirements.txt
├── requirements-dev.txt
├── run_tests.py
├── main.py            # Compatibility alias for app.main
└── .gitignore
```

Greeting, joke, website, and volume data live under `app/memory`. The application catalog and saved text data are also stored there; `things/saved_words.txt` receives recognized command words at runtime. The root `main.py` provides a compatibility import path; use `python -m app.main` to start the application.

## Docker Test Environment

The project includes a Windows-based Docker image for running the configured quality checks and application tests in a Windows environment.

The container is based on Windows Server Core with Python 3.14.7. The Dockerfile installs runtime and development requirements plus the Microsoft Visual C++ Redistributable. Its default command runs `run_tests.py`. The image is a test environment, not a documented way to run the microphone-driven assistant.

### Running Tests

Build the Docker image:

```powershell
docker build -t stiukov-tests .
docker run --rm stiukov-tests
```

`run_tests.py` runs two Ruff rule groups and `pytest tests/application`. The documentation grammar test is a separate test module and is not included in this default command. The runner currently gates its exit status on the second Ruff check and the application tests; it records but does not gate on the first quality-check result.

## Development Workflow

Run `python run_tests.py` locally, or build and run the Windows Docker image with the commands above.

For the application tests alone, run `python -m pytest tests/application`. GitHub Actions uses Python 3.11.x for lint and application tests and Python 3.14.7 in the Docker image; it also runs Hadolint.


## Notes

- The project is Windows-specific because it uses Windows APIs and components such as `winreg`, `os.startfile`, Windows audio APIs, and PowerShell.
- Speech-to-text uses faster-whisper and the current configuration requests Whisper Large with CUDA and FP16.
- Application discovery focuses on game and launcher-related entries rather than every installed application.
- Recognized command words are appended to `things/saved_words.txt` during runtime.
- Application launching and closing depend on the generated application catalog and Windows process information.
