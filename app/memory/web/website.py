"""Load website metadata used by the web command handler."""

import json
from pathlib import Path

websites_file_path = Path(__file__).parent / "websites.json"


def load_websites() -> dict[str, dict[str, str | None]]:
    """Read the configured website dictionary from disk."""
    if not websites_file_path.exists():
        return {}

    with websites_file_path.open("r", encoding="utf-8") as file:
        websites_data = json.load(file)
    return websites_data.get("websites", {})
