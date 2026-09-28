"""Coordinate application discovery and launch operations."""

from app.commands.system.applications.apps_operations import (
    close_app,
    open_app,
    search_and_save_applications,
)
from app.commands.system.applications.apps_search import launcher_search
from app.memory.system.applications.applications import (
    applications_file_exists,
    load_applications,
    save_applications,
)


def applications_handler(voice_data: str) -> bool:
    """Search for apps or open/close a matching application from spoken input."""
    if "search applications" in voice_data:
        return search_and_save_applications(
            launcher_search,
            save_applications,
        )
    if "open" in voice_data or "close" in voice_data:
        apps = load_applications()

        for app_name in apps:
            if "open " + app_name.lower() in voice_data:
                return open_app(apps, app_name)

            if "close " + app_name.lower() in voice_data:
                return close_app(apps, app_name)

    return False


def ensure_applications_file() -> None:
    """Create the applications index file when it does not exist yet."""
    if applications_file_exists():
        return

    search_and_save_applications(
        launcher_search,
        save_applications,
    )
