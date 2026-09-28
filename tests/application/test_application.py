import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from app.main import (
    handle_application,
    load_applications,
    search_and_save_launchers,
    search_launchers,
)
# =========================
# HANDLERS
# =========================



# =========================
# COMMANDS
# =========================

from app.commands.system.text import text_operations

# =========================
# MEMORY
# =========================

from app.memory.system.text import text


project_dir = Path(__file__).parent.parent.parent


def test_things_directory_exists():
    assert (project_dir / "things").exists()


@patch("app.main.launcher_search")
@patch("app.main.speak")
def test_search_and_save_launchers(
        mock_speak,
        mock_launcher_search, 
        tmp_path
    ):
    mock_launcher_search.return_value = {
        "Steam": {
            "Path": "fake_path",
            "AppID": None,
            "Protocol": None,
            "Keyword": "steam"
        }
    }    
    test_file = tmp_path / "applications.json"

    with patch("main.applications_file_path", test_file):
        assert search_and_save_launchers()

    mock_launcher_search.assert_called_once()

    assert test_file.exists()


@patch("app.main.launcher_search")
def test_failed_search_launchers(mock_search_and_save):

    mock_search_and_save.return_value = {}

    assert search_and_save_launchers() is False
    mock_search_and_save.assert_called_once()


@patch("main.search_and_save_launchers")
def test_search_launchers(mock_search_and_save):

    result = search_launchers("search applications")

    assert result
    mock_search_and_save.assert_called_once()


@patch("app.main.search_and_save_launchers")
def test_failed_seatch_launchers(mock_search_and_save):

    result = search_launchers("hi")

    assert result is False
    mock_search_and_save.assert_not_called()


def test_load_applications(tmp_path):

    test_file = tmp_path / "applications.json"

    test_data = {
        "applications": {
            "Steam": {
                "Path": "fake_path"
            }
        }
    }
    with open(test_file, "w", encoding="utf-8") as file:
        json.dump(test_data, file)

    with patch("main.applications_file_path", test_file):
        result = load_applications()

    assert result == test_data["applications"]


@patch("app.main.os.startfile")
@patch("app.main.speak")
def test_open_application(
        mock_speak,
        mock_startfile
    ):
    fake_applications = {
    "Steam": {
        "Path": "fake_path",
        "AppID": None,
        "process": "steam.exe"
        }
    }
    with patch("main.applications", fake_applications):
        result = handle_application("open steam")

    assert result is True
    mock_startfile.assert_called_once_with("fake_path")
    mock_speak.assert_called_once_with("Opening Steam")


@patch("app.main.psutil.process_iter")
@patch("app.main.speak")
def test_close_application(
        mock_speak,
        mock_process_iter
    ):
    fake_process = MagicMock()
    fake_process.info = {"name": "steam.exe"}

    fake_parent = MagicMock()
    fake_parent.name.return_value = "explorer.exe"
    fake_process.parent.return_value = fake_parent

    fake_applications = {
    "Steam": {
        "Path": "fake_path",
        "AppID": None,
        "process": "steam.exe"
        }
    }

    mock_process_iter.return_value = [fake_process]

    with patch("main.applications", fake_applications):
        result = handle_application("close steam")

    assert result is True
    mock_process_iter.assert_called_once_with(["name"])
    fake_process.terminate.assert_called_once()
    mock_speak.assert_called_once_with("Closing Steam")



def test_text_operations_with_voice_text():
    mock_save_text = MagicMock()
    voice_data = "save text to save"
    expected_text = "text to save"

    text_operations(
        voice_data,
        mock_save_text
    )

    mock_save_text.assert_called_once_with(expected_text)


@patch("app.commands.system.text.speak")
@patch("app.commands.system.text.pyperclip")
@patch("app.commands.system.text.pyautogui")
def test_text_operations_with_clipboard(
        mock_pyautogui,
        mock_pyperclip,
        mock_speak
    ):
    mock_save_text = MagicMock()
    expected_text = "text from selection"

    mock_pyperclip.paste.side_effect = ["old clipboard", expected_text]

    text_operations("save", mock_save_text)

    mock_pyautogui.hotkey.assert_called_once_with("ctrl", "c")

    mock_save_text.assert_called_once_with(
        expected_text
    )

    mock_speak.assert_called_once_with("Text is pasted")


@patch("app.commands.system.text.speak")
@patch("app.commands.system.text.pyperclip")
@patch("app.commands.system.text.pyautogui")
@patch("app.commands.system.text.record_audio")
def test_text_operations_with_record_audio(
        mock_record_audio,
        mock_pyautogui,
        mock_pyperclip,
        mock_speak
    ):
    mock_save_text = MagicMock()
    expected_text = "text to save"
    mock_record_audio.return_value = expected_text

    clipboard_check = ""
    mock_pyperclip.paste.side_effect = [clipboard_check, clipboard_check]

    text_operations("save", mock_save_text)

    mock_pyautogui.hotkey.assert_called_once_with("ctrl", "c")

    mock_record_audio.assert_called_once_with()

    mock_save_text.assert_called_once_with(
        expected_text
    )

    mock_speak.assert_called_once_with("What do you want to save?")


def test_save_text_saved_data(
    tmp_path
):
    text.text_file_path = tmp_path / "texts.json"

    text.save_text("Terraform")

    with open(text.text_file_path, "r", encoding="utf-8") as file:
        data = json.load(file)


    assert data["texts"]["1"] == "Terraform"


def test_save_text_id_generation(
    tmp_path
):
    text.text_file_path = tmp_path / "texts.json"

    text.save_text("Terraform")
    text.save_text("Ansible")

    with open(text.text_file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    assert data["texts"]["1"] == "Terraform"
    assert data["texts"]["2"] == "Ansible"


def test_save_text_empty_file(
    tmp_path
):
    text.text_file_path = tmp_path / "texts.json"

    data = {
        "texts": {}
    }

    with open(text.text_file_path, "w", encoding="utf-8") as file:
        json.dump(data, file)

    text.save_text("Terraform")

    with open(text.text_file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    assert data["texts"]["1"] == "Terraform"