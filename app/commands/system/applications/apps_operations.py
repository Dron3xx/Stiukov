"""Manage saved application records and launch/close actions."""

import subprocess
from collections.abc import Callable
from os import startfile

import psutil

from app.voice.speak import speak


def search_and_save_applications(
    launcher_search: Callable[[], dict[str, dict[str, str | None]]],
    save_applications: Callable[[dict[str, dict[str, str | None]]], bool],
) -> bool:
    """Search the OS for launchers and save the results to the applications file."""
    apps_to_save = launcher_search()

    if not apps_to_save:
        print("No apps found")
        return False

    speak("Found and saved launchers to applications file")
    print(f"Saved {len(apps_to_save)} launchers to applications.json")
    return save_applications(apps_to_save)


def open_app(apps: dict[str, dict[str, str | None]], app_name: str) -> bool:
    """Open an application either by file path or Windows AppID shortcut."""
    path = apps[app_name]["Path"]
    app_id = apps[app_name]["AppID"]
    if not path:
        subprocess.run(
            ["explorer.exe", f"shell:AppsFolder\\{app_id}"],
            check=False,
        )
    else:
        startfile(path)

    speak("Opening " + app_name)
    return True


def close_app(apps: dict[str, dict[str, str | None]], app_name: str) -> bool:
    """Close a running app by matching its process name to the saved metadata."""
    process_name = apps[app_name]["process"].lower()
    for process in psutil.process_iter(["name"]):
        try:
            name = process.info["name"]

            if name and name.lower() == process_name:
                parent = process.parent()

                if parent and parent.name().lower() != process_name:
                    process.terminate()
                    speak("Closing " + app_name)
                    return True

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    speak(app_name + " is not running")
    return True
