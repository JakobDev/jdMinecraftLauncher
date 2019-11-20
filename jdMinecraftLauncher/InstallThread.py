from PyQt5.QtCore import QThread, pyqtSignal
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
        self.env = env

    def __del__(self):
        self.wait()

    def setup(self, profile):
        self.profile = profile

    def run(self):
        minecraft_launcher_lib.install.install_minecraft_version(self.profile.getVersionID(),self.env.dataPath,callback=self.callback)

