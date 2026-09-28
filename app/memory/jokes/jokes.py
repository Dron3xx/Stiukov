"""Load joke prompts and responses."""

import json
from pathlib import Path

jokes_file_path = Path(__file__).parent / "jokes.json"


def load_jokes() -> dict[str, dict[str, str]]:
    """Read the joke catalog from disk."""
    if not jokes_file_path.exists():
        return {}

    with jokes_file_path.open("r", encoding="utf-8") as file:
        jokes_data = json.load(file)
    return jokes_data.get("jokes", {})
