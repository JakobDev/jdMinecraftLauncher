from ...ui_compiled.ModpackTab import Ui_ModpackTab
from PyQt6.QtWidgets import QWidget, QFileDialog
from ...utils.InstallMrpack import installMrpack
from PyQt6.QtCore import QCoreApplication
from typing import TYPE_CHECKING
import os


if TYPE_CHECKING:
    from ...Environment import Environment
    from .MainWindow import MainWindow


class ModpackTab(QWidget, Ui_ModpackTab):
    def __init__(self, env: "Environment", mainWindow: "MainWindow") -> None:
        super().__init__()

        self.setupUi(self)

        self._env = env
        self._mainWindow = mainWindow

        self.browseButton.clicked.connect(self._browseButtonClicked)

        self._mainWindow.installThread.started.connect(lambda: self.browseButton.setEnabled(False))
        self._mainWindow.installThread.finished.connect(lambda: self.browseButton.setEnabled(True))

    def _browseButtonClicked(self) -> None:
        fileFilter = QCoreApplication.translate("ModpackTab", "Modrinth modpack") + " (*.mrpack);;"
        fileFilter += QCoreApplication.translate("ModpackTab", "All Files") + " (*)"

        path = QFileDialog.getOpenFileName(self, directory=os.path.expanduser("~"), filter=fileFilter)[0]

        if path == "":
            return

        installMrpack(self._mainWindow, self._env, self._mainWindow.installThread, path)
