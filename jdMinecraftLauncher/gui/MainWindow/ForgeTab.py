from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QPushButton
from PyQt6.QtCore import Qt, QCoreApplication
from typing import TYPE_CHECKING
import minecraft_launcher_lib
import sys


if TYPE_CHECKING:
    from ...Environment import Environment
    from .MainWindow import MainWindow


class ForgeTab(QTableWidget):
    def __init__(self, env: "Environment", mainWindow: "MainWindow") -> None:
        super().__init__(0, 2)

        self._env = env
        self._mainWindow = mainWindow

        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.horizontalHeader().hide()
        self.verticalHeader().hide()

        count = 0
        minecraft_version_check = {}

        try:
            forgeVersionList = minecraft_launcher_lib.forge.list_forge_versions()
        except Exception:
            print("Could not get Forge Versions", file=sys.stderr)
            return

        for i in forgeVersionList:
            minecraft_version, _ = i.split("-", 1)

            if minecraft_version in minecraft_version_check or not minecraft_launcher_lib.forge.supports_automatic_install(i):
                continue

            minecraft_version_check[minecraft_version] = True

            versionItem = QTableWidgetItem(i)
            versionItem.setFlags(versionItem.flags() ^ Qt.ItemFlag.ItemIsEditable)

            installButton = QPushButton(QCoreApplication.translate("ForgeTab", "Install"))

            installButton.clicked.connect(self._installButtonClicked)

            self.insertRow(count)
            self.setItem(count, 0, versionItem)
            self.setCellWidget(count, 1, installButton)

            count += 1

    def _installForgeVersion(self, forgeVersion: str) -> None:
        self._mainWindow.installThread.setupForgeInstallation(forgeVersion)
        self._mainWindow.installThread.start()

        self._mainWindow.setInstallButtonsEnabled(False)

    def _installButtonClicked(self) -> None:
        for i in range(self.rowCount()):
            if self.cellWidget(i, 1) == self.sender():
                self._installForgeVersion(self.item(i, 0).text())
                return

    def setButtonsEnabled(self, enabled: bool) -> None:
        for i in range(self.rowCount()):
            self.cellWidget(i, 1).setEnabled(enabled)
