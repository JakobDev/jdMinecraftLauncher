from PyQt6.QtWidgets import QMessageBox
import minecraft_launcher_lib
from typing import Dict, List
import subprocess
import platform
import requests
import shutil
import socket
import json
import copy
import os


def openFile(path: str):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


def saveProfiles(env):
    profileList = []
    for a in env.profiles:
        b = vars(a)
        c = {}
        for key, value in b.items():
            if value != env:
                c[key] = value
        profileList.append(c)
    with open(os.path.join(env.dataPath, "jdMinecraftLauncher","profiles.json"), 'w', encoding='utf-8') as f:
        json.dump({"selectedProfile":env.selectedProfile,"profileList":profileList}, f, ensure_ascii=False, indent=4)


def showMessageBox(title: str, text: str, env, callback=None):
    messageBox = QMessageBox()
    messageBox.setWindowTitle(env.translate(title))
    messageBox.setText(env.translate(text))
    messageBox.setStandardButtons(QMessageBox.Ok)
    if callback != None:
        messageBox.buttonClicked.connect(callback)
    messageBox.exec_()


def hasInternetConnection() -> bool:
    try:
        socket.create_connection(("api.mojang.com", 80))
        return True
    except OSError:
        return False
    return False


def downloadFile(url: str, path: str):
    if os.path.isfile(path):
        return
    try:
        os.makedirs(os.path.dirname(path))
    except:
        pass
    r = requests.get(url, stream=True)
    with open(path, 'wb') as f:
        r.raw.decode_content = True
        shutil.copyfileobj(r.raw, f)


def getAccountDict(information_dict: Dict) -> Dict:
    return {
        "name": information_dict["name"],
        "accessToken": information_dict["access_token"],
        "refreshToken": information_dict["refresh_token"],
        "uuid": information_dict["id"]
    }


def findJavaRuntimes() -> List[str]:
    runtimeList = []
    if os.path.isdir("/usr/lib/jvm"):
        for i in os.listdir("/usr/lib/jvm"):
            if not os.path.islink(os.path.join("/usr/lib/jvm", i)):
                runtimeList.append(os.path.join("/usr/lib/jvm", i, "bin", "java"))
    if os.path.isdir("/usr/lib/sdk"):
        for i in os.listdir("/usr/lib/sdk"):
            runtimeList.append(os.path.join("/usr/lib/sdk", i, "bin", "java"))
    return runtimeList


def isFlatpak() -> bool:
    return os.path.isdir("/app")
