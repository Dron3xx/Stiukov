from pathlib import Path
import json


websites_file_path = Path(__file__).parent / "websites.json"


def load_websites():
    if not websites_file_path.exists():
        return {}

    with open(websites_file_path, "r", encoding="utf-8") as file:
        websites_data = json.load(file)
    return websites_data.get("websites", {})