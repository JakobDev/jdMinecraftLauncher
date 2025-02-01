from .Constants import NewsTypeSetting, DisplayServerSetting
from typing import Optional, Any
import traceback
import json
import sys
import os


class Settings():
    def __init__(self) -> None:
        self._default_settings: dict[str, Any] = {
            "language": "default",
            "newsType": NewsTypeSetting.MINECRAFT,
            "newsFeedURL": "https://jakobdev.codeberg.page/blog/rss.xml",
            "newsFeedDefaultBrowser": True,
            "newsURL": "https://www.minecraft.net",
            "enableMultiLaunch": False,
            "extractNatives": False,
            "windowIconProgress": True,
            "customMinecraftDir": None,
            "useFlatpakSubsandbox": True,
            "checkUpdatesStartup": True,
            "displayServer": DisplayServerSetting.AUTO,
        }

        self._user_settings: dict[str, Any] = {}
        self._loadError: str | None = None

    def get(self, key: str) -> Any:
        """Returns the given setting"""
        if key in self._user_settings:
            return self._user_settings[key]
        elif key in self._default_settings:
            return self._default_settings[key]
        else:
            return None

    def set(self, key: str, value: Any) -> None:
        """Set the value of a setting"""
        self._user_settings[key] = value

    def save(self, path: str) -> None:
        """Save settings into file"""
        if len(self._user_settings) == 0 and not os.path.isfile(path):
            return

        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self._user_settings, f, ensure_ascii=False, indent=4)
        except Exception:
            print(traceback.format_exc(), file=sys.stderr)

    def load(self, path: str) -> None:
        """Load settings from file"""
        if not os.path.isfile(path):
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                self._user_settings = json.load(f)
        except Exception:
            self._loadError = traceback.format_exc()
            print(self._loadError, file=sys.stderr)

    def reset(self) -> None:
        """Resets all settings to the default values"""
        self._user_settings.clear()

    def getLoadError(self) -> Optional[str]:
        return self._loadError
