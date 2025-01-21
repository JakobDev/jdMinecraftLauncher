from PyQt6.QtWidgets import QTableWidget, QAbstractItemView, QMenu, QHeaderView, QTableWidgetItem
from PyQt6.QtGui import QAction, QContextMenuEvent
from PyQt6.QtCore import Qt, QCoreApplication
from typing import TYPE_CHECKING
import shutil
import os


if TYPE_CHECKING:
    from ...Environment import Environment


class VersionEditorTab(QTableWidget):
    def __init__(self, env: "Environment") -> None:
        super().__init__(0, 2)
        self._env = env

        self._uninstallVersion = QAction(QCoreApplication.translate("VersionEditorTab", "Uninstall Version"), self)
        self._uninstallVersion.triggered.connect(self._uninstallVersionClicked)

        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setHorizontalHeaderLabels((QCoreApplication.translate("VersionEditorTab", "Minecraft Version"), QCoreApplication.translate("VersionEditorTab", "Version Type")))
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.verticalHeader().hide()
        self.setShowGrid(False)

        self.updateVersions()

    def updateVersions(self) -> None:
        if len(self._env.installedVersion) == 0:
            self._uninstallVersion.setEnabled(False)
        else:
            self._uninstallVersion.setEnabled(True)

        while self.rowCount() > 0:
            self.removeRow(0)

        count = 0
        for i in self._env.installedVersion:
            idItem = QTableWidgetItem(i["id"])
            idItem.setFlags(idItem.flags() ^ Qt.ItemFlag.ItemIsEditable)
            typeItem = QTableWidgetItem(i["type"])
            typeItem.setFlags(typeItem.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.insertRow(count)
            self.setItem(count, 0, idItem)
            self.setItem(count, 1, typeItem)
            count += 1

    def _uninstallVersionClicked(self) -> None:
        shutil.rmtree(os.path.join(self._env.minecraftDir, "versions", self._env.installedVersion[self.currentRow()]["id"]))
        del self._env.installedVersion[self.currentRow()]
        self._env.updateInstalledVersions()
        self.updateVersions()

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:  # type: ignore
        self.menu = QMenu(self)

        self.menu.addAction(self._uninstallVersion)

        self.menu.popup(event.globalPos())
