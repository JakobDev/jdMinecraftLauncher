from PyQt6.QtWidgets import QTableWidget, QAbstractItemView, QMenu, QHeaderView, QTableWidgetItem
from ...core.VersionCollection import VersionCollection
from PyQt6.QtGui import QAction, QContextMenuEvent
from PyQt6.QtCore import Qt, QCoreApplication
from ...Functions import clearTableWidget


class _TableColumns:
    VERSION = 0
    TYPE = 1


class VersionEditorTab(QTableWidget):
    def __init__(self) -> None:
        super().__init__(0, 2)

        self._versionCollection = VersionCollection.getInstance()
        self._versionCollection.versionsUpdated.connect(self._updateVersions)

        self._uninstallVersion = QAction(QCoreApplication.translate("VersionEditorTab", "Uninstall Version"), self)
        self._uninstallVersion.triggered.connect(self._uninstallVersionClicked)

        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setHorizontalHeaderLabels((QCoreApplication.translate("VersionEditorTab", "Minecraft Version"), QCoreApplication.translate("VersionEditorTab", "Version Type")))
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.verticalHeader().hide()
        self.setShowGrid(False)

        self._updateVersions()

    def _updateVersions(self) -> None:
        installedVersions = VersionCollection.getInstance().getInstalledVersions()

        if len(installedVersions) == 0:
            self._uninstallVersion.setEnabled(False)
        else:
            self._uninstallVersion.setEnabled(True)

        clearTableWidget(self)

        for row, version in enumerate(installedVersions):
            idItem = QTableWidgetItem(version["id"])
            idItem.setFlags(idItem.flags() ^ Qt.ItemFlag.ItemIsEditable)

            typeItem = QTableWidgetItem(version["type"])
            typeItem.setFlags(typeItem.flags() ^ Qt.ItemFlag.ItemIsEditable)

            self.insertRow(row)
            self.setItem(row, _TableColumns.VERSION, idItem)
            self.setItem(row, _TableColumns.TYPE, typeItem)

    def _uninstallVersionClicked(self) -> None:
        version = self.item(self.currentRow(), _TableColumns.VERSION).text()
        self._versionCollection.uninstallVersion(version)

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:  # type: ignore
        menu = QMenu(self)

        menu.addAction(self._uninstallVersion)

        menu.popup(event.globalPos())
