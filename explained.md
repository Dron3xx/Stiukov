# Stiukov - Technical Explanation

## Architecture

Stiukov is a Windows desktop voice assistant implemented in Python.

The main runtime logic is located in `app/main.py`. The launcher discovery functionality is separated into `app/apps_search.py`.

The application follows a simple runtime flow:

1. Start the Python application.
2. Load paths to the JSON data files.
3. Generate the application catalog if it does not exist.
4. Load greetings, jokes, and applications.
5. Continuously listen through the default microphone.
6. Wait for a configured wake word while inactive.
7. Process recognized speech through the command dispatcher.
8. Keep the assistant active until `go to sleep` is received.

The application uses local Python and Windows APIs for control and Google Speech Recognition for speech-to-text; it does not use a separate conversational AI backend.

## 1) Project Structure

The most important runtime files are:

- `app/main.py` — main event loop, wake-word handling, speech recognition, command dispatch, application control, web commands, and volume control
- `app/apps_search.py` — Windows launcher discovery and application catalog generation
- `things/greetings.json` — greeting phrases and responses
- `things/jokes.json` — joke question and answer data
- `saved_words.txt` — runtime log of recognized command words

`things/applications.json` is generated during runtime and is not part of the checked-in repository structure.

---

## 2) Runtime Initialization

### Data paths

What this does:

- defines the locations of the application's runtime data files
- provides a common project-relative location for greetings, jokes, and application data

How it works:

`main.py` determines the project directory from the location of the Python file and creates paths for:

- `things/applications.json`
- `things/greetings.json`
- `things/jokes.json`

This avoids relying on the current working directory when locating the data files.

### Application catalog initialization

What this does:

- ensures that the application catalog exists before the application tries to load it

How it works:

At startup, the application checks whether `things/applications.json` exists.

If it does not exist, `search_and_save_launchers()` calls `launcher_search()` from `app/apps_search.py` and saves the discovered launchers as JSON.

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

The current code contains these configured variations:

```text
stuck off
stucco
stick off
sticker
sicko
stickers
tickle
sick off
stupid
take off
speaker
```

The `sick off` entry appears twice in the current list. The duplicate does not change the documented behavior, so it is represented only once here.

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

The application continuously calls `record_audio()`.

When speech is recognized:

- if the assistant is inactive, `wake_word_detector()` checks for a wake word
- if no wake word is found, the input is ignored
- if the assistant is active, or a wake word activated it, the remaining speech is passed to `respond()`

The loop is wrapped in exception handling so an unexpected runtime error is printed instead of immediately terminating the assistant.

Why this matters:

This creates the core behavior of a continuously running voice assistant rather than a one-command application.

---

## 5) Voice Input and Speech Output

### `record_audio()`

What this does:

- captures audio from the default microphone
- sends the captured audio to Google Speech Recognition
- converts the recognized text to lowercase
- returns an empty string when no speech was successfully recognized

How it works:

The function creates a microphone source through `speech_recognition`, records audio with the recognizer, and calls:

```python
recognizer.recognize_google(audio, language="en-EN")
```

The recognized text is printed and then normalized with `.lower()` before being returned.

The current implementation handles:

- `sr.UnknownValueError` when speech cannot be understood
- `sr.RequestError` when the recognition service cannot be reached

Why this matters:

Lowercase normalization gives the command handlers a consistent input format and avoids unnecessary case-sensitive comparisons.

### `speak()`

What this does:

- prints the assistant's response
- speaks the response through the local Windows text-to-speech engine

How it works:

The function initializes `pyttsx3`, configures the speech rate and volume, sends the response to the engine, waits for playback to finish, and then stops the engine.

Why this matters:

The assistant can provide both visible console feedback and spoken responses without relying on an external text-to-speech service.

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

The dispatcher first checks for:

```text
go to sleep
```

If found, it sets `assistant_active` to `False` and stops processing that command.

Otherwise, it checks the handlers in this order:

1. `search_launchers()`
2. `handle_greeting()`
3. `handle_joke()`
4. `handle_application()`
5. `handle_web_command()`
6. `handle_volume()`

Each handler returns `True` when it handles the command, causing `respond()` to return immediately.

If no handler matches, the assistant speaks the fallback message.

Why this matters:

Centralizing command routing keeps individual command implementations separate while providing a predictable processing order.

---

## 7) Runtime Word Logging

### `save_words_to_file()`

What this does:

- appends recognized command words to `saved_words.txt`

How it works:

`respond()` splits recognized speech into words and passes them to `save_words_to_file()`.

The words are appended to the project-level `saved_words.txt` file.

Why this matters:

The application maintains a simple local history of recognized command input without requiring a separate database or service.

---

## 8) Data-Driven Responses

### Greetings

The application loads greeting data from:

```text
things/greetings.json
```

`load_greetings()` reads the JSON file and returns the `greetings` collection.

`handle_greeting()` then checks the recognized speech against the configured greeting phrases and speaks the associated response when a match is found.

### Jokes

The application loads joke data from:

```text
things/jokes.json
```

`load_jokes()` reads the JSON file and returns the `jokes` collection.

`handle_joke()` checks whether the recognized speech contains the word `joke`. When it does, it selects one of the available jokes and speaks its question and answer.

Why this matters:

Keeping response content in JSON separates user-facing text from the command-processing logic. New greetings or jokes can therefore be added without changing the corresponding Python handler.

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

### `search_and_save_launchers()`

What this does:

- runs launcher discovery
- saves the results into `things/applications.json`
- informs the user about the generated catalog

How it works:

The function calls `launcher_search()`.

If no launchers are found, it returns `False`.

Otherwise, it writes the discovered application data to `things/applications.json`.

### `search applications`

What this does:

- provides a voice command for rebuilding the launcher catalog

How it works:

`search_launchers()` checks whether the recognized speech contains:

```text
search applications
```

When detected, it calls `search_and_save_launchers()` and returns `True`.

Why this matters:

The application catalog can be refreshed without manually editing the generated JSON file.

---

## 12) Application Launch and Close

### `handle_application()`

What this does:

- launches applications from the generated catalog
- closes matching running processes

How it works:

For an `open <application>` command, the function searches the loaded application definitions.

If an executable path exists, the application is started with:

```python
os.startfile(path)
```

If the entry does not have a path, the function attempts to open the Windows AppsFolder using the stored AppID.

For a `close <application>` command, the function reads the configured process name and iterates through running processes using `psutil`.

When a matching process is found and its parent process is different from the target process, it is terminated.

Why this matters:

The assistant can control locally discovered applications without maintaining hard-coded launch commands for every application.

This functionality is Windows-specific and depends on Windows process information.

---

## 13) Web Command

### `handle_web_command()`

What this does:

- opens YouTube when the user requests it

How it works:

The handler checks for:

```text
open youtube
```

and calls `webbrowser.open()` with the YouTube address.

Why this matters:

It provides a simple browser action without requiring a separate browser automation framework.

---

## 14) Volume Control

### `handle_volume()`

What this does:

- increases the master speaker volume
- decreases the master speaker volume
- mutes the default audio endpoint
- unmutes the default audio endpoint

How it works:

The function obtains the default Windows speaker endpoint through `pycaw`.

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

The repository contains:

- `requirements.txt` — runtime dependencies
- `requirements-dev.txt` — development and testing dependencies
- `run_tests.py` — test/lint execution entry point
- `tests/` — project tests
- `Dockerfile` — container configuration present in the repository
- `saved_words.txt` — local runtime word log
- `things/` — JSON data used by the assistant

The documentation describes only behavior that is part of the current application flow. Repository files that are not involved in the current runtime behavior should not be interpreted as active assistant features solely because they exist.

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
Speech Recognition
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
2. Google Speech Recognition
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

The application is currently a Windows-specific Python voice assistant based on speech recognition, pattern matching, local Windows APIs, and generated application metadata.

## Summary

Stiukov combines voice input, local text-to-speech, command dispatch, Windows application discovery, application control, browser interaction, and system-volume control in a single Python application.

The architecture separates the main assistant runtime from launcher discovery, while JSON files keep response content and generated application metadata outside the main command-handling logic.

The current implementation uses Google Speech Recognition for speech-to-text, local Windows APIs for system control, and does not use a separate conversational AI backend.
