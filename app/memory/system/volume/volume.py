from pathlib import Path
import json


volume_file_path = Path(__file__).parent / "volume.json"


def load_volume():
    if not volume_file_path.exists():
        return {}

    with open(volume_file_path, "r", encoding="utf-8") as file:
        volume_data = json.load(file)
    return volume_data.get("volume", {})