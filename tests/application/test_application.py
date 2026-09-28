import json
from pathlib import Path
from unittest.mock import MagicMock, patch


# =========================
# HANDLERS
# =========================

from app.handlers.applications import (
    applications_handler,
    ensure_applications_file
)

# =========================
# COMMANDS
# =========================

from app.commands.system.applications.apps_operations import (
    search_and_save_applications,
    open_app,
    close_app
)
from app.commands.system.applications.apps_search import launcher_search
from app.commands.system.text import text_operations

# =========================
# MEMORY
# =========================

from app.memory.system.applications.applications import (
    load_applications,
    save_applications,
    applications_file_exists
)
from app.memory.system.text import text


# =========================
# APPLICATIONS MODULE TESTS
# =========================

@patch("app.commands.system.applications.apps_operations.speak")
def test_search_and_save_applications(
        mock_speak,
    ):
    mock_launcher_search = MagicMock()
    mock_save_applications = MagicMock()
    found_applications  = {
        "Steam": {
            "Path": "fake_path",
            "AppID": None,
            "Protocol": None,
            "Keyword": "steam"
        }
    }

    mock_launcher_search.return_value = found_applications

    assert search_and_save_applications(
        mock_launcher_search,
        mock_save_applications
    )

    mock_launcher_search.assert_called_once()
    mock_save_applications.assert_called_once_with(found_applications)


def test_failed_search_launchers():
    mock_launcher_search = MagicMock()
    mock_save_applications = MagicMock()

    mock_launcher_search.return_value = {}

    assert search_and_save_applications(mock_launcher_search, mock_save_applications) is False

    mock_launcher_search.assert_called_once()
    mock_save_applications.assert_not_called()


@patch("app.commands.system.applications.apps_operations.startfile")
@patch("app.commands.system.applications.apps_operations.speak")
def test_open_app(
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

    assert open_app(fake_applications, "Steam")

    mock_startfile.assert_called_once_with("fake_path")
    mock_speak.assert_called_once_with("Opening Steam")


@patch("app.commands.system.applications.apps_operations.psutil.process_iter")
@patch("app.commands.system.applications.apps_operations.speak")
def test_close_app(
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

    assert close_app(fake_applications, "Steam")

    mock_process_iter.assert_called_once_with(["name"])
    fake_process.terminate.assert_called_once()
    mock_speak.assert_called_once_with("Closing Steam")

@patch("app.handlers.applications.search_and_save_applications")
def test_applications_handler(mock_search_and_save):

    result = applications_handler("search applications")

    assert result
    mock_search_and_save.assert_called_once()


@patch("app.handlers.applications.search_and_save_applications")
def test_failed_applications_handler(mock_search_and_save):

    result = applications_handler("hi")

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

    with patch("app.memory.system.applications.applications.applications_file_path", test_file):
        result = load_applications()

    assert result == test_data["applications"]


def test_save_applications(tmp_path):

    test_file = tmp_path / "applications.json"

    test_data = {
        "applications": {
            "Steam": {
                "Path": "fake_path"
            }
        }
    }

    with patch("app.memory.system.applications.applications.applications_file_path", test_file):
        save_applications(test_data)

    with open(test_file, "r", encoding="utf-8") as file:
        data_to_test = json.load(file)

    assert data_to_test["applications"] == test_data


@patch("app.memory.system.applications.applications.applications_file_path")
def test_applications_file_exists(
    mock_applications_file_path
):
    mock_applications_file_path.exists.return_value = True

    assert applications_file_exists()


@patch("app.memory.system.applications.applications.applications_file_path")
def test_failed_applications_file_exists(
    mock_applications_file_path
):
    mock_applications_file_path.exists.return_value = False

    assert applications_file_exists() == False


# =========================
# TEXTS MODULE TESTS
# =========================

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