from PyQt6.QtCore import pyqtClassInfo, pyqtSlot, pyqtProperty  # type:ignore[attr-defined]
from jdMinecraftLauncher.RunMinecraft import getMinecraftCommand
from PyQt6.QtDBus import QDBusConnection, QDBusAbstractAdaptor
from .core.ProfileCollection import ProfileCollection
from typing import TYPE_CHECKING
from .Globals import Globals
import json
import sys
import os


if TYPE_CHECKING:
    from .gui.MainWindow.MainWindow import MainWindow


with open(os.path.join(os.path.dirname(__file__), "DBusInterface.xml"), "r", encoding="utf-8") as f:
    interface = f.read()


@pyqtClassInfo("D-Bus Interface", "page.codeberg.JakobDev.jdMinecraftLauncher")  # type: ignore
@pyqtClassInfo("D-Bus Introspection", interface)  # type: ignore
class DBusService(QDBusAbstractAdaptor):
    def __init__(self, mainWindow: "MainWindow") -> None:
        super().__init__(mainWindow)
        QDBusConnection.sessionBus().registerObject("/", self)

        if not QDBusConnection.sessionBus().registerService("page.codeberg.JakobDev.jdMinecraftLauncher"):
            print(QDBusConnection.sessionBus().lastError().message(), file=sys.stderr)

        self._mainWindow = mainWindow

    @pyqtSlot(str, result=bool)  # type: ignore
    def LaunchProfile(self, name: str) -> bool:
        profile = ProfileCollection.getInstance().getProfileByName(name)
        if profile:
            self._mainWindow.launchProfile(profile)
            return True
        else:
            return False

    @pyqtSlot(result=list)  # type: ignore
    def ListProfiles(self) -> list[str]:
        profileList = []
        for profile in ProfileCollection.getInstance().getProfileList():
            profileList.append(profile.name)
        return profileList

    @pyqtSlot(result=str)  # type: ignore
    def GetProfile(self) -> str:
        return json.dumps(ProfileCollection.getInstance().getSelectedProfile().toDict())

    @pyqtSlot(str, result=list)  # type: ignore
    def GetMinecraftCommand(self, profile_id: str) -> list[str]:
        profile = ProfileCollection.getInstance().getProfileByID(profile_id)
        if profile:
            return getMinecraftCommand(profile, "")["command"]
        return []

    @pyqtSlot(result=str)  # type: ignore
    def GetVersion(self) -> str:
        return Globals.launcherVersion

    @pyqtProperty(bool)  # type: ignore
    def MainWindowVisible(self) -> bool:
        return self._mainWindow.isVisible()

    @MainWindowVisible.setter  # type: ignore
    def MainWindowVisible(self, show: bool) -> None:
        self._mainWindow.setVisible(show)
