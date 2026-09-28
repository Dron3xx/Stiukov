"""Load configured greeting text."""

import json
from pathlib import Path

jokes_file_path = Path(__file__).parent / "greetings.json"


def load_greetings() -> dict[str, str]:
    """Read the greeting catalog from disk."""
    if not jokes_file_path.exists():
        return {}

    with jokes_file_path.open("r", encoding="utf-8") as file:
        greetings_data = json.load(file)
    return greetings_data.get("greetings", {})
