# Stiukov project explanation

This file explains how the Stiukov voice assistant is structured, how a spoken command moves through the program, and how the supporting configuration files are used.

## 1) Project purpose

Stiukov is a Windows desktop voice assistant written in Python. The current implementation combines:

- microphone input and Google speech recognition
- text-to-speech responses
- wake-word detection
- application launching and process management
- browser launching
- Windows system-volume control
- JSON-based greetings, jokes, and application settings
- Windows registry inspection and executable metadata discovery through `apps_search.py`

The main program is `Stiukov.py`. The separate `apps_search.py` script explores installed applications and executable files; it is not imported by the assistant. The `things` directory contains data that can be changed without editing the command-handling code.

## 2) Python dependencies

The required packages are listed in `requirements.txt`:

```text
speechrecognition
pyttsx3
keyboard
pyautogui
pyperclip
psutil
opencv-python
numpy
Pillow
pycaw
tensorflow
```

What these packages provide:

- `SpeechRecognition` captures microphone audio and sends it to Google's recognition service.
- `pyttsx3` converts assistant responses into speech locally.
- `psutil` finds and terminates configured Windows processes.
- `pycaw` controls the Windows audio endpoint.
- `opencv-python`, `numpy`, `Pillow`, and `tensorflow` provide computer-vision and machine-learning dependencies for planned or extended functionality.
- `keyboard`, `pyautogui`, and `pyperclip` provide desktop-control capabilities for future commands.

Why this matters:

- the project is Windows-specific because it uses Windows registry access, `os.startfile`, `win32api`, and Windows audio APIs
- speech recognition requires an internet connection
- microphone access and the installed audio drivers must be available before the program can run

## 3) Runtime paths and configuration

The program builds paths relative to the location of `Stiukov.py`:

```python
current_directory = os.path.dirname(os.path.abspath(__file__))
things_directory = os.path.join(current_directory, "things")

applications_file_path = os.path.join(things_directory, "applications.json")
greetings_file_path = os.path.join(things_directory, "greetings.json")
jokes_file_path = os.path.join(things_directory, "jokes.json")
```

What this does:

- finds the project directory even when the program is started from another working directory
- points the loader functions to the three JSON files in `things`
- keeps configuration paths independent of a particular username or installation folder

The recognized words are saved to `saved_words.txt`, also relative to the project directory.

## 4) Wake-word detection and assistant state

The assistant uses the `assistant_active` global variable to track whether it should respond to commands.

```python
assistant_active = False

def wake_word_detector(voice_data):
    global assistant_active

    wake_word = is_stiukov(voice_data)

    if wake_word:
        assistant_active = True
        voice_data = re.sub(
            rf"\b{re.escape(wake_word)}\b",
            "",
            voice_data
        ).strip()

    return voice_data
```

`is_stiukov()` checks several phrases that speech recognition may produce for the assistant name, including `speaker`, `stucco`, and `sticker`.

What this does:

- ignores ordinary speech while the assistant is asleep
- activates the assistant when a recognized wake phrase is present
- removes the wake phrase before the remaining text is sent to the command dispatcher

For example, the recognized phrase `speaker open youtube` becomes `open youtube` after wake-word processing.

The assistant stays active until it receives `go to sleep`. While active, commands do not need to include a wake word.

## 5) Speech input and output

Audio is captured by `record_audio()`:

```python
def record_audio(ask=False):
    voice_data = ''
    with sr.Microphone() as source:
        if ask:
            print(ask)
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            print("Recognizing...")
            voice_data = recognizer.recognize_google(audio, language='en-EN')
        except sr.UnknownValueError:
            print('Speech not recognized')
        except sr.RequestError as e:
            print(f'Could not request results; {e}')
    return voice_data.lower()
```

What this does:

- listens through the default microphone
- sends the captured audio to Google's speech-recognition service
- converts the result to lowercase so command matching is case-insensitive
- returns an empty string when speech cannot be understood or the service request fails

Responses are handled by `speak()`. It creates a `pyttsx3` engine, sets the speech rate and volume, prints the response, speaks it, and then stops the engine.

Why this matters:

- recognition failures do not terminate the main loop
- command handlers can work with normalized text
- the same response is visible in the console and audible through the speakers

## 6) Main event loop

The bottom of `Stiukov.py` continuously connects listening, wake-word processing, and command handling:

```python
while True:
    try:
        voice_data = record_audio()

        if not voice_data:
            continue

        if not assistant_active:
            voice_data = wake_word_detector(voice_data)

            if not voice_data:
                continue

        respond(voice_data)

    except Exception as error:
        print(f"The assistant recovered from an error: {error}")
```

The lifecycle is:

1. Listen for speech.
2. Ignore empty recognition results.
3. If asleep, look for a wake word and remove it.
4. Ignore speech that did not contain a wake word.
5. Send the remaining text to `respond()`.
6. Continue listening even when an unexpected error occurs.

This keeps the assistant running as a long-lived desktop process.

## 7) Command dispatcher and priority

`respond()` first checks that the assistant is active, saves the recognized words, and then evaluates handlers in order:

```python
if "go to sleep" in voice_data:
    assistant_active = False
    speak("Going to sleep.")
    return

if search_applications(voice_data):
    return

if handle_greeting(voice_data):
    return

if handle_joke(voice_data):
    return

if handle_application(voice_data):
    return

if handle_web_command(voice_data):
    return

if handle_volume(voice_data):
    return

speak("I can't help you with it yet")
```

What this does:

- handles sleep mode before all other commands
- stops after the first handler reports a match
- provides a spoken fallback for unsupported phrases

The order is important. A handler that returns `True` prevents later handlers from processing the same command.

## 8) Greetings and jokes

Greetings are loaded from `things/greetings.json`:

```json
{
  "greetings": {
    "hello": "Hello there!",
    "hi": "Hi!",
    "hey": "Hey, how can I help you?"
  }
}
```

`handle_greeting()` loops through the configured phrases and speaks the associated response when a phrase appears in the recognized text.

Jokes are loaded from `things/jokes.json`. Each joke contains a `question` and an `answer`; `handle_joke()` chooses one entry at random when the command contains `joke`.

Why this matters:

- new greetings and jokes can be added as data
- response content is separated from Python control flow
- the joke response changes between requests instead of always using one fixed value

## 9) Application launching and closing

Applications are configured in `things/applications.json`:

```json
{
  "applications": {
    "notepad": {
      "process": "notepad.exe",
      "path": "notepad.exe"
    }
  }
}
```

`handle_application()` supports two command forms:

- `open <application>` starts the configured path with `os.startfile`
- `close <application>` searches running processes with `psutil` and terminates a matching child process

When an application is not running, the assistant says that it is not running.

The sample entries for Calculator, Opera, and Edge contain `YOUR_PATH_HERE`. Those entries must be replaced with valid local paths before they can be opened. Notepad uses `notepad.exe`, which Windows can resolve directly.

Why this matters:

- application names and process names are kept outside the handler logic
- process matching uses the configured executable name rather than assuming every application closes the same way
- invalid placeholder paths are a configuration issue, not a problem with the command parser

## 10) Browser and volume commands

`handle_web_command()` opens YouTube in the default browser:

```python
if "open youtube" in voice_data:
    wb.open("https://www.youtube.com")
    speak("Opening YouTube.")
    return True
```

`handle_volume()` uses the Windows default speaker endpoint from `pycaw`.

Supported commands:

- `volume up` increases the master volume by 10 percentage points, capped at 100%
- `volume down` decreases it by 10 percentage points, capped at 0%
- `mute` enables mute
- `unmute` disables mute

The volume handler reads the current scalar value before changing it, so repeated volume commands remain within the valid Windows range.

## 11) Word logging

Every non-empty recognized command is split into words and appended to `saved_words.txt`:

```python
def save_words_to_file(words):
    saved_words_file_path = os.path.join(current_directory, "saved_words.txt")
    with open(saved_words_file_path, "a", encoding="utf-8") as file:
        file.write(" ".join(words) + "\n")
```

What this does:

- preserves each recognized command as one line
- appends instead of replacing previous entries
- uses UTF-8 when writing the log

This file can be used as a simple record of recognized input or as a starting point for future vocabulary and command improvements.

## 12) Application search status

`search_applications()` listens for `search applications` and enumerates application paths registered under the current user's Windows App Paths registry key. The registry code was added to `Stiukov.py` as a voice-triggered inspection command.

At present, it prints each discovered subkey, path, and whether the path exists. It does not add the discovered applications to `applications.json`, launch them, or return `True`; the command therefore continues to the unsupported-command response.

This is an exploratory feature rather than a complete application-search workflow. A future implementation could return a list of discovered applications or use the results to update the configuration file.

## 13) Standalone executable search

`apps_search.py` is a separate Windows-only exploration script. It has two search paths:

- `search_registry_apps()` enumerates the current user's App Paths registry entries, checks whether each executable exists, and calls `read_file_metadata()`.
- `search_disk()` walks the configured Steam, Blizzard, cracks, and Xbox folders, prints every `.exe` file it finds, and reads its file description metadata.

The script uses `ctypes` to call functions from Windows `Version.dll`:

```python
version = ctypes.WinDLL("Version.dll")
version.GetFileVersionInfoW.argtypes = [
    ctypes.c_wchar_p,
    ctypes.c_uint32,
    ctypes.c_uint32,
    ctypes.c_void_p
]
```

What this does:

- loads the Windows version-information library
- declares the argument and return types for the functions used later
- allows the script to locate the executable's language/code-page translation and query its `FileDescription`

The script currently calls `search_disk()` when run, so its configured folders should be reviewed before execution. `analyze_apps()` combines both searches but is not the automatic entry point.

## 14) Overall result

The current assistant works as follows:

1. The microphone captures speech.
2. Google's recognition service converts it into lowercase text.
3. A recognized wake phrase activates the assistant when it is asleep.
4. The command is logged to `saved_words.txt`.
5. The dispatcher checks sleep, registry search, greeting, joke, application, web, and volume behavior.
6. The first matching handler performs the action and speaks a response.
7. Unsupported commands receive a fallback response.
8. The loop continues listening after normal commands and recoverable errors.

The project can be installed and started with:

```powershell
python -m pip install -r requirements.txt
python Stiukov.py
```

The assistant is currently a focused Windows automation project. The imported vision, desktop-control, and machine-learning libraries provide room for future capabilities, while the implemented command set is centered on voice interaction, applications, registry inspection, YouTube, greetings, jokes, and system audio. The standalone search script provides additional exploratory executable discovery but does not yet persist its findings as assistant configuration.
