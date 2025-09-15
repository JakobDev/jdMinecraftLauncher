from .core.VersionCollection import VersionCollection
from .Constants import LauncherVisibility
import minecraft_launcher_lib
from .Globals import Globals
from typing import Type


class Profile:
    def __init__(self, id: str, name: str) -> None:
        self.id = id
        self.name = name
        self.version = ""
        self.useLatestVersion = True
        self.useLatestSnapshot = False
        self.customGameDirectory = False
        self.gameDirectoryPath = Globals.minecraftDir
        self.customResolution = False
        self.resolutionX = "854"
        self.resolutionY = "480"
        self.customLauncherVisibility = False
        self.launcherVisibility = LauncherVisibility.HIDE
        self.enableSnapshots = False
        self.enableBeta = False
        self.enableAlpha = False
        self.customExecutable = False
        self.executable = minecraft_launcher_lib.utils.get_java_executable()
        self.customArguments = False
        self.arguments = "-Xms512M -Xmx512M"
        self.serverConnect = False
        self.serverIP = ""
        self.serverPort = ""
        self.demoMode = False
        self.disableMultiplayer = False
        self.disableChat = False
        self.hasMinecraftOptions = False
        self.minecraftOptions = ""
        self.useGameMode = False

    def getVersionID(self) -> str:
        if self.useLatestVersion:
            return VersionCollection.getInstance().getLatestRelease()
        elif self.useLatestSnapshot:
            return VersionCollection.getInstance().getLatestSnapshot()
        else:
            return self.version

    def getGameDirectoryPath(self) -> str:
        if self.customGameDirectory:
            return self.gameDirectoryPath
        else:
            return Globals.minecraftDir

    def getJavaPath(self) -> str:
        if self.customExecutable:
            return self.executable
        else:
            return "java"

    def setCustomVersion(self, version: str) -> None:
        self.useLatestVersion = False
        self.useLatestSnapshot = False
        self.version = version

    @classmethod
    def load(cls: Type["Profile"], objects: dict, profileVersion: int) -> "Profile":
        profile = Profile(objects["id"], objects["name"])

        profile.version = objects["version"]
        profile.useLatestVersion = objects["useLatestVersion"]
        profile.customGameDirectory = objects["customGameDirectory"]
        profile.gameDirectoryPath = objects["gameDirectoryPath"]
        profile.customResolution = objects["customResolution"]
        profile.resolutionX = objects["resolutionX"]
        profile.resolutionY = objects["resolutionY"]
        profile.customLauncherVisibility = objects["customLauncherVisibility"]
        profile.launcherVisibility = objects["launcherVisibility"]
        profile.enableSnapshots = objects["enableSnapshots"]
        profile.enableBeta = objects["enableBeta"]
        profile.enableAlpha = objects["enableAlpha"]
        profile.customExecutable = objects["customExecutable"]
        profile.executable = objects["executable"]
        profile.customArguments = objects["customArguments"]
        profile.arguments = objects["arguments"]
        profile.serverConnect = objects["serverConnect"]
        profile.serverIP = objects["serverIP"]
        profile.serverPort = objects["serverPort"]
        profile.demoMode = objects["demoMode"]
        profile.disableMultiplayer = objects.get("disableMultiplayer", False)
        profile.disableChat = objects.get("disableMultiplayer", False)
        profile.hasMinecraftOptions = objects.get("hasMinecraftOptions", False)
        profile.minecraftOptions = objects.get("minecraftOptions", "")
        profile.useGameMode = objects.get("useGameMode", False)

        if profileVersion == 1:
            try:
                profile.version = profile.version.split(" ")[1]
            except IndexError:
                pass

        return profile

    def toDict(self) -> dict:
        data = {}
        for key, value in vars(self).items():
            if isinstance(value, int) or isinstance(value, bool) or isinstance(value, str):
                data[key] = value
        return data
