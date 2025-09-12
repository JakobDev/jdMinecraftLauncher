from ...ui_compiled.ModpackTab import Ui_ModpackTab
from PyQt6.QtWidgets import QWidget, QFileDialog
from ...utils.InstallMrpack import installMrpack
from ...InstallThread import InstallThread
from PyQt6.QtCore import QCoreApplication
from typing import TYPE_CHECKING
import os


if TYPE_CHECKING:
    from .MainWindow import MainWindow


class ModpackTab(QWidget, Ui_ModpackTab):
    def __init__(self, mainWindow: "MainWindow") -> None:
        super().__init__()

        self.setupUi(self)

        self._mainWindow = mainWindow
        self._installThread = InstallThread.getInstance()

        self.browseButton.clicked.connect(self._browseButtonClicked)

        self._installThread.started.connect(lambda: self.browseButton.setEnabled(False))
        self._installThread.finished.connect(lambda: self.browseButton.setEnabled(True))

    def _browseButtonClicked(self) -> None:
        fileFilter = QCoreApplication.translate("ModpackTab", "Modrinth modpack") + " (*.mrpack);;"
        fileFilter += QCoreApplication.translate("ModpackTab", "All Files") + " (*)"

        path = QFileDialog.getOpenFileName(self, directory=os.path.expanduser("~"), filter=fileFilter)[0]

        if path == "":
            return

        installMrpack(self._mainWindow, path)
