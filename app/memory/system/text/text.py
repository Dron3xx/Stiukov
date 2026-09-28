"""Persist user-saved text snippets."""

import json
from pathlib import Path

text_file_path = Path(__file__).parent / "texts.json"


def load_text() -> dict[str, str]:
    """Read the saved text catalogue from disk."""
    if not text_file_path.exists():
        return {}

    with text_file_path.open("r", encoding="utf-8") as file:
        text_data = json.load(file)
    return text_data.get("texts", {})


def save_text(text_to_save: str) -> bool:
    """Append text_to_save to the saved texts collection."""
    texts = load_text()
    if not texts:
        texts = {"1": text_to_save}
    else:
        i = max(int(key) for key in texts)
        i += 1
        texts[str(i)] = text_to_save

    with text_file_path.open("w", encoding="utf-8") as file:
        json.dump(
            {"texts": texts},
            file,
            indent=4,
            ensure_ascii=False,
        )

    return True
