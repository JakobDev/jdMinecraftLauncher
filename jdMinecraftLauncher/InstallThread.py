from PyQt6.QtCore import QThread, pyqtSignal
from typing import Optional, TYPE_CHECKING
import minecraft_launcher_lib
import traceback


if TYPE_CHECKING:
    from .Environment import Environment
    from .Profile import Profile


class InstallThread(QThread):
    progress_max = pyqtSignal("int")
    progress = pyqtSignal("int")
    text = pyqtSignal("QString")

    def __init__(self, env: "Environment") -> None:
        QThread.__init__(self)
        self.callback: minecraft_launcher_lib.types.CallbackDict = {
            "setStatus": lambda text: self.text.emit(text),
            "setMax": lambda max_progress: self.progress_max.emit(max_progress),
            "setProgress": lambda progress: self.progress.emit(progress),
        }
        self.forgeVersion: str | None = None
        self.fabricVersion: str | None = None
        self._currentError: str | None = None
        self._versionNotFound = False
        self.env = env

    def __del__(self) -> None:
        self.wait()

    def _setupAll(self) -> None:
        self.forgeVersion = None
        self.fabricVersion = None
        self._currentError = None
        self._versionNotFound = False

    def setup(self, profile: "Profile") -> None:
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

    def isVersionNotFound(self) -> bool:
        return self._versionNotFound

    def run(self) -> None:
        try:
            if self.forgeVersion:
                minecraft_launcher_lib.forge.install_forge_version(self.forgeVersion, self.env.minecraftDir, callback=self.callback)
            elif self.fabricVersion:
                minecraft_launcher_lib.fabric.install_fabric(self.fabricVersion, self.env.minecraftDir, callback=self.callback)
            else:
                minecraft_launcher_lib.install.install_minecraft_version(self.profile.getVersionID(), self.env.minecraftDir, callback=self.callback)
        except minecraft_launcher_lib.exceptions.VersionNotFound:
            self._versionNotFound = True
        except Exception:
            self._currentError = traceback.format_exc()
