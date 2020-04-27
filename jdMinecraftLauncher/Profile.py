import minecraft_launcher_lib

class Profile():
    def __init__(self, name, env):
        self.env = env
        self.name = name
        self.version = ""
        self.useLatestVersion = True
        self.customGameDirectory = False
        self.gameDirectoryPath = env.dataPath
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

    def getVersion(self):
        if self.useLatestVersion:
            return "release " + self.env.versions["latest"]["release"]
        else:
            return self.version

    def getVersionID(self):
        versiontype, versionid = self.getVersion().split(" ")
        return versionid

    def getGameDirectoryPath(self):
        if self.customGameDirectory:
            return self.gameDirectoryPath
        else:
            return self.env.dataPath

    def getJavaPath(self):
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
