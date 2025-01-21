from PyQt6.QtWidgets import QTableWidget, QAbstractItemView, QHeaderView, QTableWidgetItem, QMenu, QMessageBox
from ...Shortcut import canCreateShortcuts, askCreateShortcut
from PyQt6.QtGui import QContextMenuEvent, QAction
from PyQt6.QtCore import Qt, QCoreApplication
from ...Functions import openFile
from typing import TYPE_CHECKING
from ...Profile import Profile


if TYPE_CHECKING:
    from ...Environment import Environment
    from .MainWindow import MainWindow


class ProfileEditorTab(QTableWidget):
    def __init__(self, env: "Environment", mainWindow: "MainWindow") -> None:
        super().__init__(0, 2)

        self._env = env
        self._mainWindow = mainWindow
        self._profileList: list["Profile"] = []

        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setHorizontalHeaderLabels((QCoreApplication.translate("ProfileEditorTab", "Profile Name"), QCoreApplication.translate("ProfileEditorTab", "Minecraft Version")))
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.verticalHeader().hide()
        self.setShowGrid(False)

        self.updateProfiles()

    def updateProfiles(self) -> None:
        self._profileList.clear()
        while self.rowCount() > 0:
            self.removeRow(0)

        count = 0
        for i in self._env.profileCollection.profileList:
            nameItem = QTableWidgetItem(i.name)
            nameItem.setFlags(nameItem.flags() ^ Qt.ItemFlag.ItemIsEditable)
            if i.useLatestVersion:
                versionItem = QTableWidgetItem(QCoreApplication.translate("ProfileEditorTab", "(Latest version)"))
            elif i.useLatestSnapshot:
                versionItem = QTableWidgetItem(QCoreApplication.translate("ProfileEditorTab", "(Latest snapshot)"))
            else:
                versionItem = QTableWidgetItem(i.version)
            versionItem.setFlags(versionItem.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.insertRow(count)
            self.setItem(count, 0, nameItem)
            self.setItem(count, 1, versionItem)
            self._profileList.append(i)
            count += 1

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:  # type: ignore
        self.menu = QMenu(self)

        addProfile = QAction(QCoreApplication.translate("ProfileEditorTab", "Add Profile"), self)
        addProfile.triggered.connect(self._addProfile)
        self.menu.addAction(addProfile)

        editProfile = QAction(QCoreApplication.translate("ProfileEditorTab", "Edit Profile"), self)
        editProfile.triggered.connect(self._editProfile)
        self.menu.addAction(editProfile)

        copyProfile = QAction(QCoreApplication.translate("ProfileEditorTab", "Copy Profile"), self)
        copyProfile.triggered.connect(self._copyProfile)
        self.menu.addAction(copyProfile)

        removeProfile = QAction(QCoreApplication.translate("ProfileEditorTab", "Remove Profile"), self)
        removeProfile.triggered.connect(self._removeProfile)
        self.menu.addAction(removeProfile)

        openGameFolder = QAction(QCoreApplication.translate("ProfileEditorTab", "Open Game Folder"), self)
        openGameFolder.triggered.connect(lambda: openFile(self._env.profileCollection.profileList[self.currentRow()].getGameDirectoryPath()))
        self.menu.addAction(openGameFolder)

        if canCreateShortcuts():
            createShortcut = QAction(QCoreApplication.translate("ProfileEditorTab", "Create Shortcut"), self)
            createShortcut.triggered.connect(lambda: askCreateShortcut(self._env, self._mainWindow, self._env.profileCollection.profileList[self.currentRow()]))
            self.menu.addAction(createShortcut)

        self.menu.popup(event.globalPos())

    def _addProfile(self) -> None:
        self._mainWindow.profileWindow.loadProfile(Profile(QCoreApplication.translate("ProfileEditorTab", "New Profile"), self._env), True)
        self._mainWindow.profileWindow.open()

    def _editProfile(self) -> None:
        self._mainWindow.profileWindow.loadProfile(self._env.profileCollection.profileList[self.currentRow()], False)
        self._mainWindow.profileWindow.open()

    def _copyProfile(self) -> None:
        self._mainWindow.profileWindow.loadProfile(self._env.profileCollection.profileList[self.currentRow()], True, True)
        self._mainWindow.profileWindow.open()

    def _removeProfile(self) -> None:
        if len(self._env.profileCollection.profileList) == 1:
            QMessageBox.critical(self._mainWindow, QCoreApplication.translate("ProfileEditorTab", "Can't delete Profile"), QCoreApplication.translate("ProfileEditorTab", "You can't delete all Profiles. At least one Profile must stay."))
        else:
            self._env.profileCollection.removeProfileById(self._profileList[self.currentRow()].id)
            self._mainWindow.updateProfileList()
