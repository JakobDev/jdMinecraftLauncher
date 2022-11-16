from PyQt6.QtCore import QThread, pyqtSignal
import minecraft_launcher_lib


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
        self.env = env

    def __del__(self):
        self.wait()

    def setup(self, profile):
        self.profile = profile
        self.startMinecraft = True

    def setupForgeInstallation(self, forgeVersion: str):
        self.forgeVersion = forgeVersion
        self.startMinecraft = False

    def setupFabricInstallation(self, fabricVersion: str):
        self.fabricVersion = fabricVersion
        self.startMinecraft = False

    def shouldStartMinecraft(self) -> bool:
        return self.startMinecraft

    def run(self):
        if self.forgeVersion:
            minecraft_launcher_lib.forge.install_forge_version(self.forgeVersion, self.env.minecraftDir, callback=self.callback)
            self.forgeVersion = None
        elif self.fabricVersion:
            minecraft_launcher_lib.fabric.install_fabric(self.fabricVersion, self.env.minecraftDir, callback=self.callback)
            self.fabricVersion = None
        else:
            minecraft_launcher_lib.install.install_minecraft_version(self.profile.getVersionID(),self.env.minecraftDir,callback=self.callback)

