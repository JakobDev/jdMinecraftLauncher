from PyQt6.QtCore import QThread, pyqtSignal
import minecraft_launcher_lib
from typing import Optional
import traceback


class InstallThread(QThread):
    progress_max = pyqtSignal("int")
    progress = pyqtSignal("int")
    text = pyqtSignal("QString")

    def __init__(self, env):
        QThread.__init__(self)
        self.callback = {
            "setStatus": lambda text: self.text.emit(text),
            "setMax": lambda max_progress: self.progress_max.emit(max_progress),
            "setProgress": lambda progress: self.progress.emit(progress),
        }
        self.forgeVersion = None
        self.fabricVersion = None
        self._currentError = None
        self.env = env

    def __del__(self):
        self.wait()

    def _setupAll(self) -> None:
        self.forgeVersion = None
        self.fabricVersion = None
        self._currentError = None

    def setup(self, profile) -> None:
        self._setupAll()
        self.profile = profile
        self.startMinecraft = True

    def setupForgeInstallation(self, forgeVersion: str) -> None:
        self._setupAll()
        self.forgeVersion = forgeVersion
        self.startMinecraft = False

    def setupFabricInstallation(self, fabricVersion: str) -> None:
        self._setupAll()
        self.fabricVersion = fabricVersion
        self.startMinecraft = False

    def shouldStartMinecraft(self) -> bool:
        return self.startMinecraft

    def getError(self) -> Optional[str]:
        return self._currentError

    def run(self) -> None:
        try:
            if self.forgeVersion:
                minecraft_launcher_lib.forge.install_forge_version(self.forgeVersion, self.env.minecraftDir, callback=self.callback)
            elif self.fabricVersion:
                minecraft_launcher_lib.fabric.install_fabric(self.fabricVersion, self.env.minecraftDir, callback=self.callback)
            else:
                minecraft_launcher_lib.install.install_minecraft_version(self.profile.getVersionID(),self.env.minecraftDir,callback=self.callback)
        except Exception:
            self._currentError = traceback.format_exc()
