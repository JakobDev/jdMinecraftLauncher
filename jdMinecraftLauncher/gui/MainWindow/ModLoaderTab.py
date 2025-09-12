from PyQt6.QtWidgets import QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QPushButton
from PyQt6.QtCore import Qt, QThread, QCoreApplication, pyqtSignal
from ...InstallThread import InstallThread
import minecraft_launcher_lib


class _TableColumns:
    VERSION = 0
    BUTTON = 1


class _ModLoaderThread(QThread):
    loaded = pyqtSignal(list)

    def __init__(self, modLoader: minecraft_launcher_lib.mod_loader.ModLoader) -> None:
        super().__init__()

        self._modLoader = modLoader

    def run(self) -> None:
        versionList = self._modLoader.get_minecraft_versions(True)
        self.loaded.emit(versionList)


class _ModLoaderTable(QTableWidget):
    def __init__(self, modLoader: minecraft_launcher_lib.mod_loader.ModLoader) -> None:
        super().__init__(0, 2)

        self._buttonEnabled = True
        self._modLoader = modLoader
        self._loadThread = _ModLoaderThread(modLoader)
        self._installThread = InstallThread.getInstance()

        self.horizontalHeader().setSectionResizeMode(_TableColumns.VERSION, QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(_TableColumns.BUTTON, QHeaderView.ResizeMode.Stretch)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.horizontalHeader().hide()
        self.verticalHeader().hide()

        self.setEnabled(False)

        self._installThread.started.connect(lambda: self._setButtonsEnabled(False))
        self._installThread.finished.connect(lambda: self._setButtonsEnabled(True))
        self._loadThread.loaded.connect(self._versionsLoaded)

        self._loadThread.start()

    def _versionsLoaded(self, versionList: list[str]) -> None:
        for count, currentVersion in enumerate(versionList):
            versionItem = QTableWidgetItem(currentVersion)
            versionItem.setFlags(versionItem.flags() ^ Qt.ItemFlag.ItemIsEditable)

            installButton = QPushButton(QCoreApplication.translate("ModLoaderTab", "Install"))
            installButton.setEnabled(self._buttonEnabled)

            installButton.clicked.connect(self._installButtonClicked)

            self.insertRow(count)
            self.setItem(count, _TableColumns.VERSION, versionItem)
            self.setCellWidget(count, _TableColumns.BUTTON, installButton)

        self.setEnabled(True)

    def _installButtonClicked(self) -> None:
        for row in range(self.rowCount()):
            if self.cellWidget(row, _TableColumns.BUTTON) == self.sender():
                self._installThread.setupModLoaderInstall(self._modLoader.get_id(), self.item(row, _TableColumns.VERSION).text())
                self._installThread.start()
                return

    def _setButtonsEnabled(self, enabled: bool) -> None:
        self._buttonEnabled = enabled

        for row in range(self.rowCount()):
            self.cellWidget(row, _TableColumns.BUTTON).setEnabled(enabled)


class ModLoaderTab(QTabWidget):
    def __init__(self) -> None:
        super().__init__()

        self.tabBar().setDocumentMode(True)
        self.tabBar().setExpanding(True)

        for loaderID in minecraft_launcher_lib.mod_loader.list_mod_loader():
            modLoader = minecraft_launcher_lib.mod_loader.get_mod_loader(loaderID)

            self.addTab(_ModLoaderTable(modLoader), modLoader.get_name())
