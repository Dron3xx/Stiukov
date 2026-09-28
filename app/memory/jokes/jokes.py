from pathlib import Path
import json


jokes_file_path = Path(__file__).parent / "jokes.json"


def load_jokes():
    if not jokes_file_path.exists():
        return {}

    with open(jokes_file_path, "r", encoding="utf-8") as file:
        jokes_data = json.load(file)
    return jokes_data.get("jokes", {})