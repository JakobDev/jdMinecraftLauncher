from ...ui_compiled.AboutTab import Ui_AboutTab
from PyQt6.QtWidgets import QWidget
from ...Functions import openFile
from typing import TYPE_CHECKING
import minecraft_launcher_lib
import webbrowser


if TYPE_CHECKING:
    from ...Environment import Environment


class AboutTab(QWidget, Ui_AboutTab):
    def __init__(self, env: "Environment") -> None:
        super().__init__()

        self.setupUi(self)

        self.versionLabel.setText(self.versionLabel.text().replace("{{version}}", env.launcherVersion))
        self.libLabel.setText(self.libLabel.text().replace("{{version}}", minecraft_launcher_lib.utils.get_library_version()))

        self.viewSourceButton.clicked.connect(lambda: webbrowser.open("https://codeberg.org/JakobDev/jdMinecraftLauncher"))
        self.openMinecraftDirectoryButton.clicked.connect(lambda: openFile(env.minecraftDir))
        self.openDataDirectoryButton.clicked.connect(lambda: openFile(env.dataDir))
