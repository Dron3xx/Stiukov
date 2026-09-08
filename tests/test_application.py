from pathlib import Path
import json
from unittest.mock import patch, MagicMock
import main
from main import (
    search_and_save_launchers, 
    search_launchers, 
    load_applications, 
    handle_application
)

project_dir = Path(__file__).parent.parent


def test_things_directory_exists():
    assert (project_dir / "things").exists()


@patch("main.launcher_search")
def test_search_and_save_launchers(
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


@patch("main.launcher_search")
def test_failed_search_launchers(mock_search_and_save):

    mock_search_and_save.return_value = {}

    assert search_and_save_launchers() is False
    mock_search_and_save.assert_called_once()


@patch("main.search_and_save_launchers")
def test_search_launchers(mock_search_and_save):

    result = search_launchers("search applications")

    assert result
    mock_search_and_save.assert_called_once()


@patch("main.search_and_save_launchers")
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


@patch("main.os.startfile")
@patch("main.speak")
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


@patch("main.psutil.process_iter")
@patch("main.speak")
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
    