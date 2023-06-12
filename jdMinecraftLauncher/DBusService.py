from jdMinecraftLauncher.RunMinecraft import getMinecraftCommand
from PyQt6.QtCore import pyqtClassInfo, pyqtSlot, pyqtProperty
from PyQt6.QtDBus import QDBusConnection, QDBusAbstractAdaptor
from PyQt6.QtWidgets import QApplication
from typing import TYPE_CHECKING
import json
import sys
import os


if TYPE_CHECKING:
    from jdMinecraftLauncher.Environment import Environment


with open(os.path.join(os.path.dirname(__file__), "DBusInterface.xml"), "r", encoding="utf-8") as f:
    interface = f.read()

@pyqtClassInfo("D-Bus Interface", "page.codeberg.JakobDev.jdMinecraftLauncher")
@pyqtClassInfo("D-Bus Introspection", interface)
class DBusService(QDBusAbstractAdaptor):
    def __init__(self, env: "Environment", parent: QApplication):
        super().__init__(parent)
        QDBusConnection.sessionBus().registerObject("/", parent)

        if not QDBusConnection.sessionBus().registerService("page.codeberg.JakobDev.jdMinecraftLauncher"):
            print(QDBusConnection.sessionBus().lastError().message(), file=sys.stderr)

        self._env = env

    @pyqtSlot(str, result=bool)
    def LaunchProfile(self, name: str) -> bool:
        profile = self._env.profileCollection.getProfileByName(name)
        if profile:
            self._env.mainWindow.launchProfile(profile)
            return True
        else:
            return False

    @pyqtSlot(result=list)
    def ListProfiles(self):
        profileList = []
        for i in self._env.profiles:
            profileList.append(i.name)
        return profileList

    @pyqtSlot(result=str)
    def GetProfile(self):
        return json.dumps(self._env.profileCollection.getSelectedProfile().toDict())

    @pyqtSlot(str, result=list)
    def GetMinecraftCommand(self, profile_id: str):
        profile = self._env.profileCollection.getProfileByID(profile_id)
        if profile:
            return getMinecraftCommand(profile, self._env, "")

    @pyqtSlot(result=str)
    def GetVersion(self):
        return self._env.launcherVersion

    @pyqtProperty(bool)
    def MainWindowVisible(self):
        return self._env.mainWindow.isVisible()

    @MainWindowVisible.setter
    def MainWindowVisible(self, show: bool):
        self._env.mainWindow.setVisible(show)
