"""Load the configured volume command mappings."""

import json
from pathlib import Path

volume_file_path = Path(__file__).parent / "volume.json"


def load_volume() -> dict[str, str]:
    """Read the available volume command mappings from disk."""
    if not volume_file_path.exists():
        return {}

    with volume_file_path.open("r", encoding="utf-8") as file:
        volume_data = json.load(file)
    return volume_data.get("volume", {})
