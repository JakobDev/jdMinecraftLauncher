from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QPushButton
from PyQt6.QtCore import Qt, QCoreApplication
from typing import TYPE_CHECKING
import minecraft_launcher_lib
import sys


if TYPE_CHECKING:
    from ...Environment import Environment
    from .MainWindow import MainWindow


class FabricTab(QTableWidget):
    def __init__(self, env: "Environment", mainWindow: "MainWindow") -> None:
        super().__init__(0, 2)

        self._env = env
        self._mainWindow = mainWindow

        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.horizontalHeader().hide()
        self.verticalHeader().hide()

        try:
            fabricVersionList = minecraft_launcher_lib.fabric.get_all_minecraft_versions()
        except Exception:
            print("Could not get Fabric Versions", file=sys.stderr)
            return

        count = 0
        for i in fabricVersionList:
            if not i["stable"]:
                continue

            versionItem = QTableWidgetItem(i["version"])
            versionItem.setFlags(versionItem.flags() ^ Qt.ItemFlag.ItemIsEditable)

            installButton = QPushButton(QCoreApplication.translate("FabricTab", "Install"))

            installButton.clicked.connect(self._installButtonClicked)

            self.insertRow(count)
            self.setItem(count, 0, versionItem)
            self.setCellWidget(count, 1, installButton)

            count += 1

    def _installFabricVersion(self, fabricVersion: str) -> None:
        self._mainWindow.installThread.setupFabricInstallation(fabricVersion)
        self._mainWindow.installThread.start()

        self._mainWindow.setInstallButtonsEnabled(False)

    def _installButtonClicked(self) -> None:
        for i in range(self.rowCount()):
            if self.cellWidget(i, 1) == self.sender():
                self._installFabricVersion(self.item(i, 0).text())
                return

    def setButtonsEnabled(self, enabled: bool) -> None:
        for i in range(self.rowCount()):
            self.cellWidget(i, 1).setEnabled(enabled)
