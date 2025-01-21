from PyQt6.QtWidgets import QTableWidget, QHeaderView, QComboBox, QApplication
from typing import Dict, List, Any, TYPE_CHECKING
import subprocess
import platform
import requests
import shutil
import socket
import json
import sys
import os


if TYPE_CHECKING:
    from jdMinecraftLauncher.Environment import Environment


def openFile(path: str) -> None:
    if platform.system() == "Windows":
        os.startfile(path)  # type: ignore
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


def saveProfiles(env: "Environment") -> None:
    if env.args.dont_save_data:
        return

    profileList = []
    for a in env.profiles:
        b = vars(a)
        c = {}
        for key, value in b.items():
            if value != env:
                c[key] = value
        profileList.append(c)
    with open(os.path.join(env.dataDir, "profiles.json"), 'w', encoding='utf-8') as f:
        json.dump({"selectedProfile": env.selectedProfile, "profileList": profileList}, f, ensure_ascii=False, indent=4)


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
