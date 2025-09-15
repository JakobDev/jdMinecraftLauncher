from ...ui_compiled.AboutTab import Ui_AboutTab
from PyQt6.QtWidgets import QWidget
from ...Functions import openFile
from ...Globals import Globals
import minecraft_launcher_lib
import webbrowser


class AboutTab(QWidget, Ui_AboutTab):
    def __init__(self) -> None:
        super().__init__()

        self.setupUi(self)

        self.versionLabel.setText(self.versionLabel.text().replace("{{version}}", Globals.launcherVersion))
        self.libLabel.setText(self.libLabel.text().replace("{{version}}", minecraft_launcher_lib.utils.get_library_version()))

        self.viewSourceButton.clicked.connect(lambda: webbrowser.open("https://codeberg.org/JakobDev/jdMinecraftLauncher"))
        self.openMinecraftDirectoryButton.clicked.connect(lambda: openFile(Globals.minecraftDir))
        self.openDataDirectoryButton.clicked.connect(lambda: openFile(Globals.dataDir))
