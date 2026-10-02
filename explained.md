# Stiukov - Technical Explanation

## Architecture

Stiukov is a Windows desktop voice assistant implemented in Python.

The runtime entry point is `app/main.py`. It coordinates the voice loop and dispatches recognized text to handlers in `app/handlers/`. Handlers match requests and connect command implementations in `app/commands/` with persisted data in `app/memory/`. Voice input, activation state, and speech output are in `app/voice/`.

The application follows a simple runtime flow:

1. Start `python -m app.main`.
2. Ensure the application catalog exists, generating it from Windows sources when needed.
3. Initialize microphone capture, Silero VAD, and the configured Whisper model outside test mode.
4. Transcribe detected English speech and normalize the returned text to lowercase.
5. While inactive, wait for a configured wake-word variation; then route the remaining text through `respond()`.
6. Keep processing commands until `go to sleep` deactivates the assistant.

Speech-to-text uses local `faster-whisper`; the application has no separate conversational AI backend.

## 1) Project Structure

The application is organized by responsibility:

- `app/main.py` — startup, active/inactive state checks, logging, and command dispatch
- `app/handlers/` — route recognized text to matching commands
- `app/commands/` — perform text, speech, web, volume, and Windows application actions
- `app/memory/` — load and save JSON-backed greetings, jokes, websites, volume mappings, application metadata, and saved text
- `app/voice/` — microphone capture and STT, wake-word state, and local speech output
- `tests/application/` — application behavior and architecture tests
- `tests/documentation/` — a separate LanguageTool-based Markdown check
- `benchmark/engines/` and `benchmark/recordings/` — standalone STT experiments and scenario recordings, not the assistant's runtime path

The root `main.py` is a compatibility alias for `app.main`. The recognized-word log is `things/saved_words.txt`. The application catalog is stored at `app/memory/system/applications/applications.json`; the other configurable and saved JSON data lives alongside its corresponding `app/memory` module.

---

## 2) Runtime Initialization

### Data paths

What this does:

- defines the locations of the application's runtime data files
- provides a common project-relative location for greetings, jokes, and application data

How it works:

Each memory module defines a path relative to its own file, so stored data does not depend on the process working directory. Greetings, jokes, websites, and volume mappings have JSON files in their corresponding memory packages. Saved text is written to `app/memory/system/text/texts.json`.

### Application catalog initialization

What this does:

- ensures that the application catalog exists before the application tries to load it

How it works:

At import/startup, `app.main` calls `ensure_applications_file()` unless `PYTEST_CURRENT_TEST` is set. The handler checks whether `app/memory/system/applications/applications.json` exists.

If it does not exist, the handler passes `launcher_search()` and `save_applications()` to `search_and_save_applications()`. The search implementation is in `app/commands/system/applications/apps_search.py`; persistence is in `app/memory/system/applications/applications.py`.

Why this matters:

- the assistant does not require a manually maintained application list
- the catalog can reflect the current Windows environment
- application discovery is separated from command handling

---

## 3) Wake-Word and Assistant State

### `is_stiukov()`

What this does:

- checks recognized speech for configured variations of the assistant's name
- returns the first matching wake-word variant

The current code keeps the wake-word variations in `app/voice/activation/active.py`. They include speech-recognition spellings such as `stukov`, `stuck off`, `stucco`, and `stick off`; the list is source-controlled and can be changed there.

How it works:

The function iterates through the configured wake words and creates a regular-expression pattern for each one. When a match is found, the matching phrase is returned.

Why this matters:

- speech recognition can produce different interpretations of the assistant's name
- supporting multiple configured variants makes activation more tolerant of recognition differences

### `wake_word_detector()`

What this does:

- checks whether the recognized speech contains a configured wake word
- activates the assistant when one is found
- removes the detected wake word from the speech before command processing

How it works:

The function calls `is_stiukov()`.

When a wake word is found:

1. `assistant_active` is set to `True`
2. the detected wake word is removed from the recognized text
3. the remaining text is returned to the main loop

Why this matters:

The wake word and command can be spoken as part of the same recognized phrase. Removing the wake word allows the remaining command to be passed directly to `respond()`.

---

## 4) Main Event Loop

What this does:

- continuously listens for speech
- waits for activation when the assistant is inactive
- passes recognized commands to the dispatcher
- recovers from runtime exceptions without terminating the application

How it works:

When `app.main` runs as the entry point, its loop continuously calls the public `record_audio(ask: str | None = None) -> str` function from `app.voice.record_audio`.

When speech is recognized:

- if the assistant is inactive, `wake_word_detector()` checks for and removes a wake word
- if no wake word is found, the input is ignored
- otherwise, the remaining speech is passed to `respond()`

The loop is wrapped in exception handling, so an unexpected runtime error is printed instead of immediately terminating the assistant.

Why this matters:

This creates the core behavior of a continuously running voice assistant rather than a one-command application.

---

## 5) Voice Input and Speech Output

### `record_audio()`

What this does:

- captures audio from the default microphone
- detects speech with Silero VAD and transcribes it with faster-whisper
- converts the recognized text to lowercase
- returns the recognized text after a speech segment ends

How it works:

`record_audio(ask: str | None = None) -> str` forwards the request to a module-level `AudioCapture` instance. Outside test mode, that instance is constructed when `app.voice.record_audio` is imported. `AudioCapture` owns the model, `sounddevice` stream, audio queue, VAD iterator, and frame buffer.

The capture is mono at 16 kHz. `sounddevice` calls `audio_callback()`, which enqueues input arrays. The recording loop flattens each queued chunk into a persistent NumPy frame buffer. When at least 512 samples are available, it removes one 512-sample frame for Silero VAD and keeps any remaining samples for later processing.

The VAD iterator is configured with a 500 ms minimum silence and a 100 ms speech pad. A pre-audio buffer retains up to four frames (128 ms at 16 kHz). On a speech-start result, the previous buffered frames are added before the speech frames. On an end result, the accumulated audio is transcribed with `self.model.transcribe(..., language="en")`; segment text is joined with spaces, lowercased, and returned.

`AudioCapture` initializes `WhisperModel("large", device="cuda", compute_type="float16")`, so actual transcription requires the configured CUDA environment. The model and microphone stream are initialized once for the module-level capture object.

The test fixture sets `STIUKOV_TESTING=1`. In that mode, the audio libraries are not imported and the `AudioCapture` instance is not created; tests that exercise audio call sites mock `record_audio` instead of capturing from a microphone.

Why this matters:

Lowercase normalization gives the command handlers a consistent input format and avoids unnecessary case-sensitive comparisons.

### `speak()`

What this does:

- prints the assistant's response
- speaks the response through the local Windows text-to-speech engine

How it works:

The function initializes `pyttsx3`, configures the speech rate and volume, sends the response to the engine, waits for playback to finish, and then stops the engine.

Why this matters:

The assistant can provide both visible console feedback and spoken responses without relying on an external speech synthesis service.

---

## 6) Command Dispatch

### `respond()`

What this does:

- verifies that the assistant is active
- records recognized words
- checks commands in a defined order
- sends matching input to specialized handlers
- provides a fallback response when no handler matches

How it works:

`respond()` returns immediately if `is_active()` is false. For active input, it appends recognized words to the log and first checks for:

```text
go to sleep
```

If found, it sets `assistant_active` to `False` and stops processing that command.

Otherwise, it checks the handlers in this order:

1. `text_handler()`
2. `greetings_handler()`
3. `jokes_handler()`
4. `applications_handler()`
5. `web_handler()`
6. `volume_handler()`

Each handler returns `True` when it handles the command, causing `respond()` to return immediately.

If no handler matches, the assistant speaks the fallback message.

Why this matters:

Centralizing command routing keeps individual command implementations separate while providing a predictable processing order.

---

## 7) Runtime Word Logging

### `save_words_to_file()`

What this does:

- appends recognized command words to `things/saved_words.txt`

How it works:

`respond()` splits recognized speech into words and passes them to `save_words_to_file()`.

The words are appended to the project-level `things/saved_words.txt` file.

Why this matters:

The application maintains a simple local history of recognized command input without requiring a separate database or service.

---

## 8) Data-Driven Responses

### Greetings

The application loads greeting data from:

```text
app/memory/greetings/greetings.json
```

`load_greetings()` reads the JSON file and returns the `greetings` collection.

`greetings_handler()` checks the recognized speech against the configured phrases and calls `greeting_command()` to speak the associated response when a match is found.

### Jokes

The application loads joke data from:

```text
app/memory/jokes/jokes.json
```

`load_jokes()` reads the JSON file and returns the `jokes` collection.

`jokes_handler()` checks whether the recognized speech contains the word `joke`. When it does, `joke_command()` selects one of the available jokes and speaks its question and answer.

### Websites and volume mappings

Website records are loaded from `app/memory/web/websites.json`; `web_handler()` matches `open <name>` and `web_command()` opens the configured URL with Python's `webbrowser`. Volume phrases and their actions are loaded from `app/memory/system/volume/volume.json`; the volume command uses `pycaw` to adjust the default Windows speaker endpoint.

Why this matters:

Keeping response content and command mappings in JSON separates user-facing data from command-processing logic. Entries can be changed without rewriting the corresponding handler or command implementation.

---

## 9) Application Discovery

### `launcher_search()`

What this does:

- searches the local Windows environment for game and launcher-related applications
- collects application metadata
- removes duplicate entries
- returns the generated launcher catalog

How it works:

The discovery process uses three sources.

### Windows Registry

The registry search checks `HKEY_CLASSES_ROOT` for protocol handlers.

It ignores a configured blacklist of common system, browser, communication, and application protocols.

For matching entries, it reads the associated open command, extracts the executable path, and checks whether the path exists.

The result is kept only when the path or protocol name matches one of the configured game/launcher keywords.

### Start Menu

The Start Menu search checks the user's and system-wide Start Menu program directories.

It recursively searches for `.lnk` shortcuts and checks their names and target paths against the game/launcher keyword list.

Shortcut targets are resolved using Windows Script Host through `win32com.client`.

### AppX / PowerShell

The AppX search invokes PowerShell with:

```powershell
Get-StartApps
```

The current command specifically filters for applications whose name contains `Minecraft`.

The returned information is converted from JSON and added to the launcher catalog.

### Keyword filtering

The current game/launcher keywords are:

```text
games
gry
steam
epic
battle.net
origin
gog
ubisoft
uplay
riot
launcher
xbox
minecraft
```

Why this matters:

The project is not attempting to build a complete database of every installed Windows application. It intentionally narrows discovery toward game and launcher-related entries.

---

## 10) Launcher Deduplication

### `remove_duplicates()`

What this does:

- removes duplicate launcher entries that point to the same executable path

How it works:

For entries with an executable path, the path is normalized to lowercase and compared with paths already stored in the result.

Entries without a path are preserved.

Why this matters:

The same application can be discovered through multiple Windows sources. Deduplication prevents the generated catalog from containing multiple entries for the same executable.

---

## 11) Application Catalog Generation

### `search_and_save_applications()`

What this does:

- runs launcher discovery
- saves the results into `app/memory/system/applications/applications.json`
- informs the user about the generated catalog

How it works:

The function calls the supplied `launcher_search()` callable.

If no launchers are found, it returns `False`.

Otherwise, it writes the discovered application data through `save_applications()`.

### `search applications`

What this does:

- provides a voice command for rebuilding the launcher catalog

How it works:

`applications_handler()` checks whether the recognized speech contains:

```text
search applications
```

When detected, it calls `search_and_save_applications()` and returns its result.

Why this matters:

The application catalog can be refreshed without manually editing the generated JSON file.

---

## 12) Application Launch and Close

### `applications_handler()`, `open_app()`, and `close_app()`

What this does:

- launches applications from the generated catalog
- closes matching running processes

How it works:

For an `open <application>` command, `applications_handler()` searches the loaded application definitions and calls `open_app()` for a matching name.

If an executable path exists, the application is started with:

```python
os.startfile(path)
```

If the entry does not have a path, the function attempts to open the Windows AppsFolder using the stored AppID.

For a `close <application>` command, `applications_handler()` calls `close_app()`, which reads the configured process name and iterates through running processes using `psutil`.

When a matching process is found and its parent process is different from the target process, it is terminated.

Why this matters:

The assistant can control locally discovered applications without maintaining hard-coded launch commands for every application.

This functionality is Windows-specific and depends on Windows process information.

---

## 13) Web Command

### `web_handler()` and `web_command()`

What this does:

- opens a website configured in `app/memory/web/websites.json`

How it works:

The handler loads the website mapping and checks for:

```text
open <website name>
```

For a matching configured website, `web_command()` calls `webbrowser.open()` with its URL and speaks a confirmation.

Why this matters:

It provides a simple browser action without requiring a separate browser automation framework.

---

## 14) Volume Control

### `volume_handler()` and `volume_command()`

What this does:

- increases the master speaker volume
- decreases the master speaker volume
- mutes the default audio endpoint
- unmutes the default audio endpoint

How it works:

`volume_handler()` reads phrase-to-action mappings from `app/memory/system/volume/volume.json`. `volume_command()` obtains the default Windows speaker endpoint through `pycaw`.

For volume changes, it reads the current master volume level and changes it by `0.1`, keeping the result between `0.0` and `1.0`.

The mute state is controlled through `SetMute()`.

Supported commands are:

```text
volume up
volume down
mute
unmute
```

Why this matters:

The assistant can control basic system audio directly through Windows audio APIs.

---

## 15) Supporting Files and Tests

### Test setup

`pytest.ini` adds the repository root to the import path. Before test modules are imported, `tests/conftest.py` sets `STIUKOV_TESTING=1`. `app.voice.record_audio` checks this variable and skips importing the audio libraries and creating its `AudioCapture` instance. Tests patch audio call sites rather than opening a microphone or loading Whisper.

`tests/application/test_application.py` covers application, handler, command, and JSON persistence behavior with mocks and temporary files. `tests/application/test_architecture.py` checks layer boundaries with `pytest-archon`. `tests/documentation/test_documentation.py` contains a LanguageTool-based Markdown check over Markdown files under `tests/`; it is a separate test module and is not run by the default project runner.

### Test and lint commands

Run the configured checks locally with:

```powershell
python run_tests.py
```

The script runs two Ruff commands and then `pytest tests/application`. The first Ruff result is stored but is not included in the final exit-status condition; failures from the second Ruff command or application tests do cause a nonzero exit.

### Docker and CI

The Dockerfile uses `python:3.14.7-windowsservercore-ltsc2022`, installs both requirements files and the Microsoft Visual C++ Redistributable, copies the repository, and defaults to `python run_tests.py`:

```powershell
docker build -t stiukov-tests .
docker run --rm stiukov-tests
```

The GitHub Actions workflow runs on pushes to `main`. Ubuntu jobs use Python 3.11.x for Ruff; the quality-check job is configured with `continue-on-error`, while the code-validation job also runs Hadolint. A Windows 2022 job uses Python 3.11.x to install the requirements and run `pytest tests/application`. A separate Windows job builds and runs the Docker image and depends on code validation and pytest. Therefore, the Python used by the Docker test run (3.14.7) differs from the Python used by the CI pytest job (3.11.x).

---

## 16) Current End-to-End Flow

The current application flow is:

```text
Start application
       ↓
Check applications.json
       ↓
Generate catalog if missing
       ↓
Load greetings / jokes / applications
       ↓
Listen through microphone
       ↓
faster-whisper transcription
       ↓
Assistant inactive?
   ┌───┴───┐
  YES      NO
   ↓        ↓
Wake word  Process
detection  command
   ↓        ↓
Activated  respond()
   └───┬────┘
       ↓
Command handlers
       ↓
Speech / Windows action
       ↓
Continue listening
       ↓
"go to sleep"
       ↓
assistant_active = False
       ↓
Wait for next wake word
```

This creates a persistent local voice-assistant loop.

---

## 17) Current Implementation Summary

The current code implements:

1. continuous microphone listening
2. English speech transcription with faster-whisper (Whisper Large, CUDA, FP16)
3. configurable wake-word activation
4. an active/inactive assistant state
5. centralized command dispatch
6. JSON-based greeting and joke responses
7. Windows launcher discovery
8. generated application catalog
9. application launch and process termination
10. YouTube opening
11. Windows master-volume control
12. local logging of recognized words

The application is currently a Windows-specific Python voice assistant based on faster-whisper transcription, pattern matching, local Windows APIs, and generated application metadata.

## Summary

Stiukov combines voice input, local text-to-speech, command dispatch, Windows application discovery, application control, browser interaction, and system-volume control in a single Python application.

The architecture separates the main assistant runtime from launcher discovery, while JSON files keep response content and generated application metadata outside the main command-handling logic.

The current implementation uses faster-whisper with Whisper Large on CUDA and FP16 for speech-to-text, together with local Windows APIs for system control. It does not use a separate conversational AI backend.
