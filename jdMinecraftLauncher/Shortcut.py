from jdMinecraftLauncher.Functions import isFrozen
from PyQt6.QtCore import QCoreApplication, QTranslator
from PyQt6.QtWidgets import QWidget, QMessageBox
from typing import cast, TYPE_CHECKING
from PyQt6.QtGui import QIcon
from enum import Enum
import subprocess
import platform
import pathlib
import sys
import os


if TYPE_CHECKING:
    from jdMinecraftLauncher.Environment import Environment
    from jdMinecraftLauncher.Profile import Profile


class ShortcutLocation(Enum):
    DESKTOP = 0
    MENU = 1


def _createLinuxShortcut(env: "Environment", parent: QWidget | None, path: str, profile: "Profile") -> None:
    try:
        import desktop_entry_lib
    except ModuleNotFoundError:
        QMessageBox.critical(parent, QCoreApplication.translate("Shortcut", "desktop-entry-lib not found"), QCoreApplication.translate("Shortcut", "You need the desktop-entry-lib Python package to create a shortcut"))
        return

    entry = desktop_entry_lib.DesktopEntry()
    entry.Name.default_text = profile.name
    entry.Icon = "page.codeberg.JakobDev.jdMinecraftLauncher"
    entry.Exec = subprocess.list2cmdline(["xdg-open", "jdMinecraftLauncher:LaunchProfileByID/" + profile.id])
    entry.Categories.append("Game")
    entry.Comment.default_text = f"Start the {profile.name} profile in jdMinecraftLauncher"

    for langFile in os.listdir(os.path.join(env.currentDir, "translations")):
        if not langFile.endswith(".qm"):
            continue

        lang = langFile.removeprefix("jdMinecraftLauncher_").removesuffix(".qm")
        fullPath = os.path.join(env.currentDir, "translations", langFile)
        translator = QTranslator()
        translator.load(fullPath)
        comment = translator.translate("Shortcut", "Start the {{name}} profile in jdMinecraftLauncher").replace("{{name}}", profile.name)

        if comment != "":
            entry.Comment.translations[lang] = comment

    entry.write_file(os.path.join(path, f"page.codeberg.JakobDev.Profile.{profile.name}.desktop"))

    subprocess.run(["chmod", "+x", os.path.join(path, f"page.codeberg.JakobDev.Profile.{profile.name}.desktop")])


def _ensureWindowsUrlSchema(env: "Environment", parent: QWidget | None) -> None:
    if sys.platform != "win32":
        return
    import winreg

    # Check if the Schema already exists
    try:
        winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, "jdMinecraftLauncher").Close()
        return
    except FileNotFoundError:
        pass

    if QMessageBox.question(parent, QCoreApplication.translate("Shortcut", "Add URL Schema"), QCoreApplication.translate("Shortcut", "To make Shortcuts work, you need to add the jdMinecraftLauncher URL Schema to Windows. Should it be added?"), QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
        return

    with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Classes\jdMinecraftLauncher", 0, winreg.KEY_WRITE) as protocolKey:
        winreg.SetValueEx(protocolKey, "URL Protocol", 0, winreg.REG_SZ, "")

    with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Classes\jdMinecraftLauncher\shell\open\command", 0, winreg.KEY_WRITE) as commandKey:
        if isFrozen():
            winreg.SetValueEx(commandKey, None, 0, winreg.REG_SZ, subprocess.list2cmdline([os.path.abspath(sys.argv[0]), "%1"]))
        else:
            winreg.SetValueEx(commandKey, None, 0, winreg.REG_SZ, subprocess.list2cmdline([sys.executable, os.path.abspath(sys.argv[0]), "%1"]))


def _createWindowsShortcut(path: str, profile: "Profile") -> None:
    try:
        os.makedirs(path)
    except Exception:
        pass

    with open(os.path.join(path, f"{profile.name}.url"), "w", encoding="utf-8", newline="\r\n") as f:
        f.write("[InternetShortcut]\n")
        f.write(f"URL=jdMinecraftLauncher:LaunchProfileByID/{profile.id}\n")


def canCreateShortcuts() -> bool:
    return platform.system() in ["Linux", "Windows"]


def createShortcut(env: "Environment", parent: QWidget | None, profile: "Profile", location: ShortcutLocation) -> None:
    if platform.system() == "Linux":
        if location == ShortcutLocation.DESKTOP:
            _createLinuxShortcut(env, parent, subprocess.check_output(["xdg-user-dir", "DESKTOP"]).decode("utf-8").strip(), profile)
        elif location == ShortcutLocation.MENU:
            _createLinuxShortcut(env, parent, os.path.expanduser("~/.local/share/applications"), profile)
    elif platform.system() == "Windows":
        _ensureWindowsUrlSchema(env, parent)
        if location == ShortcutLocation.DESKTOP:
            _createWindowsShortcut(str(pathlib.Path.home() / "Desktop"), profile)
        elif location == ShortcutLocation.MENU:
            _createWindowsShortcut(os.path.join(cast(str, os.getenv("APPDATA")), "Microsoft", "Windows", "Start Menu", "Programs"), profile)


def askCreateShortcut(env: "Environment", parent: QWidget | None, profile: "Profile") -> None:
    box = QMessageBox(parent)
    box.setText(QCoreApplication.translate("Shortcut", "Select where you want to create the Shortcut"))
    box.setWindowTitle(QCoreApplication.translate("Shortcut", "Create Shortcut"))
    box.setStandardButtons(QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)

    desktopButton = box.button(QMessageBox.StandardButton.Save)
    desktopButton.setText(QCoreApplication.translate("Shortcut", "Desktop"))
    desktopButton.setIcon(QIcon())

    menuButton = box.button(QMessageBox.StandardButton.Discard)
    menuButton.setText(QCoreApplication.translate("Shortcut", "Menu"))
    menuButton.setIcon(QIcon())

    bothButton = box.button(QMessageBox.StandardButton.Cancel)
    bothButton.setText(QCoreApplication.translate("Shortcut", "Both"))
    bothButton.setIcon(QIcon())

    box.exec()

    if box.clickedButton() == desktopButton:
        createShortcut(env, parent, profile, ShortcutLocation.DESKTOP)
    elif box.clickedButton() == menuButton:
        createShortcut(env, parent, profile, ShortcutLocation.MENU)
    elif box.clickedButton() == bothButton:
        createShortcut(env, parent, profile, ShortcutLocation.DESKTOP)
        createShortcut(env, parent, profile, ShortcutLocation.MENU)
