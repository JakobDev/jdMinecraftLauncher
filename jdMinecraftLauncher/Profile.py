from typing import TYPE_CHECKING
import minecraft_launcher_lib
import uuid


if TYPE_CHECKING:
    from jdMinecraftLauncher.Environment import Environment


class Profile:
    def __init__(self, name: str, env: "Environment"):
        self.env: "Environment" = env

        self.id = self._generateProfileID()
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
        self.disableMultiplayer = False
        self.disableChat = False
        self.hasMinecraftOptions = False
        self.minecraftOptions = ""
        self.useGameMode = False

    def _generateProfileID(self) -> str:
        while True:
            current_id = str(uuid.uuid4())
            for i in self.env.profileCollection.profileList:
                if i.id == current_id:
                    break
            else:
                return current_id

    def getVersionID(self) -> str:
        if self.useLatestVersion:
            return self.env.versions["latest"]["release"]
        elif self.useLatestSnapshot:
            return self.env.versions["latest"]["snapshot"]
        else:
            return self.version

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

    @classmethod
    def load(cls, env: "Environment", objects: dict, profileVersion: int):
        profile = Profile(objects["name"], env)

        if "id" in objects:
            profile.id = objects["id"]
        else:
            profile.id = profile._generateProfileID()

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
