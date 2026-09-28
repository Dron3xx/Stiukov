"""Persist discovered application metadata on disk."""

import json
from pathlib import Path

applications_file_path = Path(__file__).parent / "applications.json"


def load_applications() -> dict[str, dict[str, str | None]]:
    """Load the saved application registry from disk."""
    if not applications_file_path.exists():
        return {}

    with applications_file_path.open(encoding="utf-8") as file:
        applications_data = json.load(file)
    return applications_data.get("applications", {})


def save_applications(apps_to_save: dict[str, dict[str, str | None]]) -> bool:
    """Write the application registry to disk."""
    with applications_file_path.open("w", encoding="utf-8") as file:
        json.dump(
            {"applications": apps_to_save},
            file,
            indent=4,
            ensure_ascii=False,
        )

    return True


def applications_file_exists() -> bool:
    """Return whether the application registry file is present."""
    return applications_file_path.exists()
