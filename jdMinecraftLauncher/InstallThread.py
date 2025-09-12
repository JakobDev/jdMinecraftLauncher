from .core.ProfileCollection import ProfileCollection
from PyQt6.QtCore import QThread, pyqtSignal
from typing import Optional, TYPE_CHECKING
import minecraft_launcher_lib
from .Globals import Globals
from enum import Enum
import traceback


if TYPE_CHECKING:
    from .Profile import Profile


class _InstallType(Enum):
    Invalid = 1
    Vanilla = 2
    ModLoader = 3
    Mrpack = 4


class InstallThread(QThread):
    _instance: Optional["InstallThread"] = None

    progressMax = pyqtSignal("int")
    progress = pyqtSignal("int")
    text = pyqtSignal("QString")

    @classmethod
    def getInstance(cls) -> "InstallThread":
        if cls._instance is None:
            cls._instance = cls()

        return cls._instance

    def __init__(self) -> None:
        QThread.__init__(self)
        self.callback: minecraft_launcher_lib.types.CallbackDict = {
            "setStatus": lambda text: self.text.emit(text),
            "setMax": lambda max_progress: self.progressMax.emit(max_progress),
            "setProgress": lambda progress: self.progress.emit(progress),
        }

        self._installType: _InstallType = _InstallType.Invalid
        self._mrpackOptionalFiles: list[str] | None = None
        self._currentProfile: "Profile" | None = None
        self._minecraftVersion: str | None = None
        self._currentError: str | None = None
        self._modLoaderID: str | None = None
        self._mrpackPath: str | None = None
        self._versionNotFound = False

    def __del__(self) -> None:
        self.wait()

    def _setupAll(self) -> None:
        self._currentError = None
        self._versionNotFound = False

    def setupVanilla(self, profile: "Profile") -> None:
        self._setupAll()

        self._installType = _InstallType.Vanilla
        self._minecraftVersion = profile.getVersionID()

    def setupModLoaderInstall(self, loaderID: str, minecraftVersion: str) -> None:
        self._setupAll()

        self._installType = _InstallType.ModLoader
        self._minecraftVersion = minecraftVersion
        self._modLoaderID = loaderID

    def setupMrpackInstall(self, profile: "Profile", path: str, optionalFiles: list[str]) -> None:
        self._setupAll()

        self._installType = _InstallType.Mrpack
        self._currentProfile = profile
        self._mrpackPath = path
        self._mrpackOptionalFiles = optionalFiles

    def shouldStartMinecraft(self) -> bool:
        return self._installType == _InstallType.Vanilla

    def getError(self) -> Optional[str]:
        return self._currentError

    def isVersionNotFound(self) -> bool:
        return self._versionNotFound

    def run(self) -> None:
        try:
            match self._installType:
                case _InstallType.Vanilla:
                    assert self._minecraftVersion is not None

                    minecraft_launcher_lib.install.install_minecraft_version(self._minecraftVersion, Globals.minecraftDir, callback=self.callback)
                case _InstallType.ModLoader:
                    assert self._minecraftVersion is not None
                    assert self._modLoaderID is not None

                    modLoader = minecraft_launcher_lib.mod_loader.get_mod_loader(self._modLoaderID)
                    modLoader.install(self._minecraftVersion, Globals.minecraftDir, callback=self.callback)
                case _InstallType.Mrpack:
                    assert self._mrpackOptionalFiles is not None
                    assert self._currentProfile is not None
                    assert self._mrpackPath is not None

                    minecraft_launcher_lib.mrpack.install_mrpack(
                        self._mrpackPath,
                        Globals.minecraftDir,
                        modpack_directory=self._currentProfile.getGameDirectoryPath(),
                        callback=self.callback,
                        mrpack_install_options={
                            "optionalFiles": self._mrpackOptionalFiles
                        }
                    )

                    self._currentProfile.setCustomVersion(minecraft_launcher_lib.mrpack.get_mrpack_launch_version(self._mrpackPath))

                    profileCollection = ProfileCollection.getInstance()
                    profileCollection.updateProfile(self._currentProfile)
                    profileCollection.save()
        except minecraft_launcher_lib.exceptions.VersionNotFound:
            self._versionNotFound = True
        except Exception:
            self._currentError = traceback.format_exc()
