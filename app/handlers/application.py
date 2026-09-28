from app.memory.system.applications.applications import (
    load_applications,
    save_applications,
    applications_file_exists
)
from app.commands.system.applications.apps_operations import (
    search_and_save_applications,
    open_app,
    close_app
)
from app.commands.system.applications.apps_search import launcher_search

def applications_handler(voice_data):
    if "search applications" in voice_data:
        return search_and_save_applications(
            launcher_search,
            save_applications
        )
    if "open" in voice_data or "close" in voice_data:
        apps = load_applications()

        for app_name in apps:
            if "open " + app_name.lower() in voice_data:
                return open_app(apps, app_name)
            
            elif "close " + app_name.lower() in voice_data:
                return close_app(apps, app_name)

    return False

def ensure_applications_file():
    if applications_file_exists():
        return

    search_and_save_applications(
        launcher_search,
        save_applications
    )