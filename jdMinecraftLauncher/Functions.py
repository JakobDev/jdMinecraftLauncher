from typing import Dict, List, TYPE_CHECKING
from PyQt6.QtWidgets import QMessageBox
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


def openFile(path: str):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


def saveProfiles(env: "Environment"):
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
        json.dump({"selectedProfile":env.selectedProfile,"profileList":profileList}, f, ensure_ascii=False, indent=4)


def hasInternetConnection() -> bool:
    try:
        socket.create_connection(("api.mojang.com", 80))
        return True
    except OSError:
        return False


def downloadFile(url: str, path: str):
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


def _addJavaRuntimeDir(path: str, runtimeList: List[str]):
    if not os.path.isdir(path):
        return
    for i in os.listdir(path):
        if not os.path.islink(os.path.join(path, i)):
            runtimeList.append(os.path.join(path, i, "bin", "java"))


def findJavaRuntimes() -> List[str]:
    runtimeList = []
    _addJavaRuntimeDir("/usr/lib/jvm", runtimeList)
    _addJavaRuntimeDir("/usr/lib/sdk", runtimeList)
    _addJavaRuntimeDir("/app/jvm", runtimeList)
    return runtimeList


def isFlatpak() -> bool:
    return os.path.isfile("/.flatpak-info")


def isFrozen() -> bool:
    """Check if the App is frozen with PyInstaller"""
    return hasattr(sys, "frozen")
