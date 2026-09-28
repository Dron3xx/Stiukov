import json
from pathlib import Path

applications_file_path = Path(__file__).parent / "applications.json"

def load_applications():
    if not applications_file_path.exists():
        return {}

    with open(applications_file_path, "r", encoding="utf-8") as file:
        applications_data = json.load(file)
    return applications_data.get("applications", {})

def save_applications(apps_to_save):
    with open(applications_file_path, "w", encoding="utf-8") as file:
        json.dump(
            {"applications": apps_to_save},
            file,
            indent=4,
            ensure_ascii=False
        )

    return True

def applications_file_exists():
    return applications_file_path.exists()