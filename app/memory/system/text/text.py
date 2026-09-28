import json
from pathlib import Path


text_file_path = Path(__file__).parent / "texts.json"


def load_text():
    if not text_file_path.exists():
        return {}

    with open(text_file_path, "r", encoding="utf-8") as file:
        text_data = json.load(file)
    return text_data.get("texts", {})


def save_text(text_to_save):
    texts = load_text()
    if not texts:
        texts = {
        "1": text_to_save
        }

    else:
        i = max(int(key) for key in texts.keys())
        i += 1
        texts[str(i)] = text_to_save

    with open(text_file_path, "w", encoding="utf-8") as file:
        json.dump(
        {"texts": texts},
        file,
        indent=4,
        ensure_ascii=False
        )

    return True
