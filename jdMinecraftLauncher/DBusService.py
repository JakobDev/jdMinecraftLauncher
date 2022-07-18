from PyQt6.QtCore import QCoreApplication, QObject, pyqtClassInfo, pyqtSlot, pyqtProperty
from PyQt6.QtDBus import QDBusConnection, QDBusAbstractAdaptor
from jdMinecraftLauncher.RunMinecraft import getMinecraftCommand
import sys
import os


with open(os.path.join(os.path.dirname(__file__), "DBusInterface.xml"), "r", encoding="utf-8") as f:
    interface = f.read()

@pyqtClassInfo("D-Bus Interface", "com.gitlab.JakobDev.jdMinecraftLauncher")
@pyqtClassInfo("D-Bus Introspection", interface)
class DBusService(QDBusAbstractAdaptor):
    def __init__(self, env, parent):
        super().__init__(parent)
        QDBusConnection.sessionBus().registerObject("/", parent)

        if not QDBusConnection.sessionBus().registerService("com.gitlab.JakobDev.jdMinecraftLauncher"):
            print(QDBusConnection.sessionBus().lastError().message(), file=sys.stderr)

        self._env = env

    @pyqtSlot(str, result=bool)
    def LaunchProfile(self, name):
        profile = self._env.getProfileByName(name)
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

    @pyqtSlot(str, result=list)
    def GetMinecraftCommand(self, name):
        profile = self._env.getProfileByName(name)
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
