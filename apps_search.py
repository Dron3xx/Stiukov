import winreg
import os
import re
from pathlib import Path
import win32com.client
import subprocess
import json


def exe_path(clear_command):
    match = re.search(r'["\']?([^"\']+\.exe)["\']?', clear_command, re.IGNORECASE)
    if match:
        return match.group(1)
    return None


def find_lnk(lnk_path):
    try:
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(str(lnk_path))
        return shortcut.TargetPath
    except Exception:
        return None


def launcher_search():
    launchers = {}

    protocol_blacklist = {
        'http', 'https', 'ftp', 'mailto', 'tel', 'file', 'ms-', 'windows',
        'chrome', 'firefox', 'opera', 'edge', 'discord', 'spotify', 'zoom',
        'skype', 'teams', 'adobe', 'vscode', 'onenote', 'outlook', 'vlc'
        }

    path_blacklist = {
            r"\steamapps\common"
        }

    game_key_words = [
        'games', 'gry', 'steam', 'epic', 'battle.net', 'origin', 
        'gog', 'ubisoft', 'uplay', 'riot', 'launcher', 'xbox', 'minecraft'
        ]
    def registry_search():
        try: 
            root_key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, "")
            value, _, _ = winreg.QueryInfoKey(root_key)

            for i in range(value):
                try:
                    key_name = winreg.EnumKey(root_key, i)

                    if any(key_name.lower().startswith(x) for x in protocol_blacklist):
                        continue

                    protocol = winreg.OpenKey(root_key, key_name)
                    try:
                        winreg.QueryValueEx(protocol, "URL protocol")
                    except FileNotFoundError:
                        winreg.CloseKey(protocol)
                        continue

                    try:
                        command_path = rf"{key_name}\shell\open\command"
                        key_command = winreg.OpenKey(root_key, command_path)
                        command, _ = winreg.QueryValueEx(key_command, "")
                        winreg.CloseKey(key_command)

                        if command:
                            clear_path = exe_path(command)

                            if clear_path and Path(clear_path).exists():
                                full_str_path = clear_path.lower()
                                
                                if any(path in clear_path for path in path_blacklist):
                                    continue

                                for x in game_key_words:
                                    if x in full_str_path or x in key_name.lower():
                                        app_name = Path(clear_path).stem
                                        launchers[app_name] = {
                                            "Path": clear_path,
                                            "AppID": None,
                                            "Protocol": f"{key_name}://",
                                            "Keyword": x,
                                        }

                                        break
                    except FileNotFoundError:
                        pass

                    winreg.CloseKey(protocol)

                except Exception:
                    continue

            winreg.CloseKey(root_key)
        except Exception as e:
            print(f"Registry read error: {e}")

        return launchers


    def start_menu_search():
        appdata = os.environ.get("APPDATA", "")
        programdata = os.environ.get("PROGRAMDATA", "")

        start_menu_path = [
            Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs",
            Path(programdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
        ]

        for start_path in start_menu_path:
            if not start_path.exists():
                continue

            for file in start_path.rglob("*"):
                if file.is_file() and file.suffix.lower() == ".lnk":
                    file_name = file.stem.lower()

                    if any(word in file_name for word in game_key_words):
                        shortcut_point = find_lnk(file)

                        if shortcut_point and Path(shortcut_point).exists():
                            shortcut_point_lower = shortcut_point.lower()

                            for x in game_key_words:
                                if x in file_name or x in shortcut_point_lower:
                                    launchers[file.stem] = {
                                        "Path": shortcut_point,
                                        "AppID": None,
                                        "Protocol": None,
                                        "Keyword": x
                                    }
                                    break

        return launchers


    def appx_search():
        ps_command = (
            'Get-StartApps | '
            'Where-Object {$_.Name -like "*Minecraft*"} | '
            'Select-Object Name, AppID | '
            'ConvertTo-Json'
        )
        results = subprocess.run(
            ["powershell", "-Command", ps_command], 
            capture_output=True, 
            text=True, 
            encoding='utf-8'
        )

        if results.stdout.strip():
            app_data = json.loads(results.stdout)

            if isinstance(app_data, dict):
                app_data = [app_data]

            for app in app_data:
                app_name = app.get("Name")
                app_id = app.get("AppID")

                launchers[app_name] = {
                    "Path": app.get("InstallLocation"),
                    "AppID": app_id,
                    "Protocol": None,
                    "Keyword": "minecraft"
                }
        else:
            print("Nothing found")
        return launchers

    appx_search()
    start_menu_search()
    registry_search()

    return launchers


def remove_duplicates(launchers):
    unique_launchers = {}

    for name, data in launchers.items():
        path = data.get("Path")

        if path:
            path_key = path.lower()

            if path_key not in [
                (app.get("Path") or "").lower()
                for app in unique_launchers.values()
                ]:
                unique_launchers[name] = data

        else:
            unique_launchers[name] = data

    return unique_launchers


if __name__ == "__main__":
    print("Searching for games launchers")
    results = launcher_search()
    results = remove_duplicates(results)

    if results:
        for app, data in results.items():
            print(f" App: [ {app} ]")
            print(f"   -> Protocol: {data['Protocol']}")
            print(f"   -> Path: {data['Path']}\n")
            print(f"   -> Keyword: {data['Keyword']}")
            if data.get("AppID"):
                print(f"   -> AppID: {data.get('AppID')}")
    else:
        print("No launcher found")