from jdMinecraftLauncher.RunMinecraft import getMinecraftCommand
from PyQt6.QtCore import pyqtClassInfo, pyqtSlot, pyqtProperty  # type:ignore[attr-defined]
from PyQt6.QtDBus import QDBusConnection, QDBusAbstractAdaptor
from PyQt6.QtWidgets import QApplication
from typing import TYPE_CHECKING
import json
import sys
import os


if TYPE_CHECKING:
    from jdMinecraftLauncher.Environment import Environment
    from .gui.MainWindow.MainWindow import MainWindow


with open(os.path.join(os.path.dirname(__file__), "DBusInterface.xml"), "r", encoding="utf-8") as f:
    interface = f.read()


@pyqtClassInfo("D-Bus Interface", "page.codeberg.JakobDev.jdMinecraftLauncher")  # type: ignore
@pyqtClassInfo("D-Bus Introspection", interface)  # type: ignore
class DBusService(QDBusAbstractAdaptor):
    def __init__(self, env: "Environment", app: QApplication, mainWindow: "MainWindow") -> None:
        super().__init__(app)
        QDBusConnection.sessionBus().registerObject("/", app)

        if not QDBusConnection.sessionBus().registerService("page.codeberg.JakobDev.jdMinecraftLauncher"):
            print(QDBusConnection.sessionBus().lastError().message(), file=sys.stderr)

        self._env = env
        self._mainWindow = mainWindow

    @pyqtSlot(str, result=bool)  # type: ignore
    def LaunchProfile(self, name: str) -> bool:
        profile = self._env.profileCollection.getProfileByName(name)
        if profile:
            self._mainWindow.launchProfile(profile)
            return True
        else:
            return False

    @pyqtSlot(result=list)  # type: ignore
    def ListProfiles(self) -> list[str]:
        profileList = []
        for i in self._env.profiles:
            profileList.append(i.name)
        return profileList

    @pyqtSlot(result=str)  # type: ignore
    def GetProfile(self) -> str:
        return json.dumps(self._env.profileCollection.getSelectedProfile().toDict())

    @pyqtSlot(str, result=list)  # type: ignore
    def GetMinecraftCommand(self, profile_id: str) -> list[str]:
        profile = self._env.profileCollection.getProfileByID(profile_id)
        if profile:
            return getMinecraftCommand(profile, self._env, "")
        return []

    @pyqtSlot(result=str)  # type: ignore
    def GetVersion(self) -> str:
        return self._env.launcherVersion

    @pyqtProperty(bool)  # type: ignore
    def MainWindowVisible(self) -> bool:
        return self._mainWindow.isVisible()

    @MainWindowVisible.setter  # type: ignore
    def MainWindowVisible(self, show: bool) -> None:
        self._mainWindow.setVisible(show)
