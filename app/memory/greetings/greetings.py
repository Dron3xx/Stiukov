from pathlib import Path
import json


jokes_file_path = Path(__file__).parent / "greetings.json"


def load_greetings():
    if not jokes_file_path.exists():
        return {}

    with open(jokes_file_path, "r", encoding="utf-8") as file:
        greetings_data = json.load(file)
    return greetings_data.get("greetings", {})