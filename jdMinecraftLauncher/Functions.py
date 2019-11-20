from PyQt5.QtWidgets import QMessageBox
import subprocess
import platform
import socket
import json
import os


def openFile(path):
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
    with open(os.path.join(env.dataPath, "jdLauncher_profiles.json"), 'w', encoding='utf-8') as f:
        json.dump(profileList, f, ensure_ascii=False, indent=4)


def showMessageBox(title, text, env, callback=None):
    messageBox = QMessageBox()
    messageBox.setWindowTitle(env.translate(title))
    messageBox.setText(env.translate(text))
    messageBox.setStandardButtons(QMessageBox.Ok)
    if callback != None:
        messageBox.buttonClicked.connect(callback)
    messageBox.exec_()

def getJavaPath():
    if platform.system() == "Windows":
        return ""
    elif platform.system() == "Darwin":
        return ""
    else:
        result = subprocess.run(['which', 'java'], stdout=subprocess.PIPE)
        return result.stdout.decode().replace("\n", "")

def hasInternetConnection():
    try:
        socket.create_connection(("api.mojang.com", 80))
        return True
    except OSError:
        return False
    return False
