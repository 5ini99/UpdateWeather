import platform
from pathlib import Path

APP_NAME = "UpdateWeather"

def is_autostart_enabled():
    if platform.system() == "Darwin":
        plist = Path.home() / f"Library/LaunchAgents/com.byron.{APP_NAME}.plist"
        return plist.exists()
    return False

def toggle_autostart(icon=None, item=None):
    pass
