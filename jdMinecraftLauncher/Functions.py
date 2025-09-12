from PyQt6.QtWidgets import QTableWidget, QHeaderView, QComboBox, QApplication
from typing import cast, Dict, List, Any
import minecraft_launcher_lib
from pathlib import Path
import subprocess
import platform
import requests
import shutil
import socket
import sys
import os


def openFile(path: str) -> None:
    if platform.system() == "Windows":
        os.startfile(path)  # type: ignore
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


def hasInternetConnection() -> bool:
    try:
        socket.create_connection(("api.mojang.com", 80))
        return True
    except OSError:
        return False


def downloadFile(url: str, path: str) -> None:
    if os.path.isfile(path):
        return
    try:
        os.makedirs(os.path.dirname(path))
    except Exception:
        pass
    r = requests.get(url, stream=True)
    with open(path, 'wb') as f:
        r.raw.decode_content = True
        shutil.copyfileobj(r.raw, f)


def getAccountDict(information_dict: Dict) -> Dict[str, str]:
    return {
        "name": information_dict["name"],
        "accessToken": information_dict["access_token"],
        "refreshToken": information_dict["refresh_token"],
        "uuid": information_dict["id"]
    }


def _addJavaRuntimeDir(path: str, runtimeList: List[str]) -> None:
    if not os.path.isdir(path):
        return
    for i in os.listdir(path):
        if not os.path.islink(os.path.join(path, i)):
            runtimeList.append(os.path.join(path, i, "bin", "java"))


def findJavaRuntimes() -> List[str]:
    runtimeList: list[str] = []
    _addJavaRuntimeDir("/usr/lib/jvm", runtimeList)
    _addJavaRuntimeDir("/usr/lib/sdk", runtimeList)
    _addJavaRuntimeDir("/app/jvm", runtimeList)
    return runtimeList


def isFlatpak() -> bool:
    return os.path.isfile("/.flatpak-info")


def isFrozen() -> bool:
    """Check if the App is frozen with PyInstaller"""
    return hasattr(sys, "frozen")


def clearTableWidget(table: QTableWidget) -> None:
    """Removes all Rows from a QTableWidget"""
    while table.rowCount() > 0:
        table.removeRow(0)


def stretchTableWidgetColumnsSize(table: QTableWidget) -> None:
    """Stretch all Columns of a QTableWidget"""
    for i in range(table.columnCount()):
        table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)


def selectComboBoxData(box: QComboBox, data: Any, default_index: int = 0) -> None:
    """Set the index to the item with the given data"""
    index = box.findData(data)
    if index == -1:
        box.setCurrentIndex(default_index)
    else:
        box.setCurrentIndex(index)


def isWayland() -> bool:
    """Returns if the Program is running in a Wayland session"""
    return QApplication.platformName() == "wayland"


def _getSystemDataDir() -> str:
    match platform.system():
        case "Windows":
            return cast(str, os.getenv("APPDATA"))
        case "Darwin":
            return os.path.join(Path.home(), "Library", "Application Support")
        case "Haiku":
            return os.path.join(Path.home(), "config", "settings")
        case _:
            if os.getenv("XDG_DATA_HOME"):
                return cast(str, os.getenv("XDG_DATA_HOME"))
            else:
                return os.path.join(Path.home(), ".local", "share")


def getDataPath() -> str:
    if os.path.isdir(os.path.join(minecraft_launcher_lib.utils.get_minecraft_directory(), "jdMinecraftLauncher")):
        return os.path.join(minecraft_launcher_lib.utils.get_minecraft_directory(), "jdMinecraftLauncher")

    dataPath = _getSystemDataDir()
    if os.path.isdir(os.path.join(dataPath, "jdMinecraftLauncher")):
        return os.path.join(dataPath, "jdMinecraftLauncher")

    return os.path.join(dataPath, "JakobDev", "jdMinecraftLauncher")
