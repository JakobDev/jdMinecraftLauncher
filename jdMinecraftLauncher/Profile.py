from typing import TYPE_CHECKING
import minecraft_launcher_lib


if TYPE_CHECKING:
    from jdMinecraftLauncher.Environment import Environment


class Profile:
    def __init__(self, name: str, env: "Environment"):
        self.env = env
        self.name = name
        self.version = ""
        self.useLatestVersion = True
        self.useLatestSnapshot = False
        self.customGameDirectory = False
        self.gameDirectoryPath = env.minecraftDir
        self.customResolution = False
        self.resolutionX = "854"
        self.resolutionY = "480"
        self.customLauncherVisibility = False
        self.launcherVisibility = 0
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
        self.useGameMode = False

    def getVersion(self) -> str:
        if self.useLatestVersion:
            return "release " + self.env.versions["latest"]["release"]
        elif self.useLatestSnapshot:
            return "snapshot " + self.env.versions["latest"]["snapshot"]
        else:
            return self.version

    def getVersionID(self) -> str:
        versiontype, versionid = self.getVersion().split(" ")
        return versionid

    def getGameDirectoryPath(self) -> str:
        if self.customGameDirectory:
            return self.gameDirectoryPath
        else:
            return self.env.minecraftDir

    def getJavaPath(self) -> str:
        if self.customExecutable:
            return self.executable
        else:
            return "java"

    def load(self, objects):
        self.name = objects["name"]
        self.version = objects["version"]
        self.useLatestVersion = objects["useLatestVersion"]
        self.customGameDirectory = objects["customGameDirectory"]
        self.gameDirectoryPath = objects["gameDirectoryPath"]
        self.customResolution = objects["customResolution"]
        self.resolutionX = objects["resolutionX"]
        self.resolutionY = objects["resolutionY"]
        self.customLauncherVisibility = objects["customLauncherVisibility"]
        self.launcherVisibility = objects["launcherVisibility"]
        self.enableSnapshots = objects["enableSnapshots"]
        self.enableBeta = objects["enableBeta"]
        self.enableAlpha = objects["enableAlpha"]
        self.customExecutable = objects["customExecutable"]
        self.executable = objects["executable"]
        self.customArguments = objects["customArguments"]
        self.arguments = objects["arguments"]
        self.serverConnect = objects["serverConnect"]
        self.serverIP = objects["serverIP"]
        self.serverPort = objects["serverPort"]
        self.demoMode = objects["demoMode"]
        self.useGameMode = objects.get("useGameMode", False)
