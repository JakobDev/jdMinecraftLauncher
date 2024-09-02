from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QMessageBox
from typing import TYPE_CHECKING
import webbrowser
import traceback
import requests
import sys


if TYPE_CHECKING:
    from ..Environment import Environment


def _checkUpdatesInternal(env: "Environment") -> None:
    latestVersion = requests.get("https://codeberg.org/api/v1/repos/JakobDev/jdMinecraftLauncher/releases/latest").json()["name"]

    if env.launcherVersion == latestVersion:
        return

    sourceforgeURL = f"https://sourceforge.net/projects/jdminecraftlauncher/files/{latestVersion}"

    if requests.head(sourceforgeURL).status_code != 200:
        return

    text = QCoreApplication.translate("UpdateChecker", "Version {{version}} of jdMinecraftLauncher is now available.").replace("{{version}}", latestVersion) + " "
    text += QCoreApplication.translate("UpdateChecker", "You are currently using version {{version}}.").replace("{{version}}", latestVersion) + " "
    text += QCoreApplication.translate("UpdateChecker", "Do you want to download the latest version?")

    if QMessageBox.question(None, QCoreApplication.translate("UpdateChecker", "New version available"), text, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
        return

    webbrowser.open(sourceforgeURL)
    sys.exit(0)


def checkUpdates(env: "Environment") -> None:
    try:
        _checkUpdatesInternal(env)
    except Exception:
        print(traceback.format_exc(), file=sys.stderr)
