from PyQt6.QtWidgets import QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QPushButton
from PyQt6.QtCore import Qt, QCoreApplication
from typing import TYPE_CHECKING
import minecraft_launcher_lib


if TYPE_CHECKING:
    from .MainWindow import MainWindow


class ModLoaderTable(QTableWidget):
    def __init__(self, mainWindow: "MainWindow", modLoader: minecraft_launcher_lib.mod_loader.ModLoader) -> None:
        super().__init__(0, 2)

        self._mainWindow = mainWindow
        self._modLoader = modLoader

        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.horizontalHeader().hide()
        self.verticalHeader().hide()

        for count, currentVersion in enumerate(modLoader.get_minecraft_versions(True)):
            versionItem = QTableWidgetItem(currentVersion)
            versionItem.setFlags(versionItem.flags() ^ Qt.ItemFlag.ItemIsEditable)

            installButton = QPushButton(QCoreApplication.translate("ModLoaderTab", "Install"))

            installButton.clicked.connect(self._installButtonClicked)

            self.insertRow(count)
            self.setItem(count, 0, versionItem)
            self.setCellWidget(count, 1, installButton)

        self._mainWindow.installThread.started.connect(lambda: self.setButtonsEnabled(False))
        self._mainWindow.installThread.finished.connect(lambda: self.setButtonsEnabled(True))

    def _installButtonClicked(self) -> None:
        for i in range(self.rowCount()):
            if self.cellWidget(i, 1) == self.sender():
                self._mainWindow.installThread.setupModLoaderInstall(self._modLoader.get_id(), self.item(i, 0).text())
                self._mainWindow.installThread.start()
                return

    def setButtonsEnabled(self, enabled: bool) -> None:
        for i in range(self.rowCount()):
            self.cellWidget(i, 1).setEnabled(enabled)


class ModLoaderTab(QTabWidget):
    def __init__(self, mainWindow: "MainWindow") -> None:
        super().__init__()

        self.tabBar().setDocumentMode(True)
        self.tabBar().setExpanding(True)

        for loaderID in minecraft_launcher_lib.mod_loader.list_mod_loader():
            modLoader = minecraft_launcher_lib.mod_loader.get_mod_loader(loaderID)

            self.addTab(ModLoaderTable(mainWindow, modLoader), modLoader.get_name())
