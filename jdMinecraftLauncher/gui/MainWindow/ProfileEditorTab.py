from PyQt6.QtWidgets import QTableWidget, QAbstractItemView, QTableWidgetItem, QMenu, QMessageBox
from ...Functions import openFile, clearTableWidget, stretchTableWidgetColumnsSize
from ...utils.Shortcut import canCreateShortcuts, askCreateShortcut
from ...core.ProfileCollection import ProfileCollection
from PyQt6.QtGui import QContextMenuEvent, QAction
from PyQt6.QtCore import Qt, QCoreApplication
from typing import TYPE_CHECKING
from ...Profile import Profile
from ...Globals import Globals


if TYPE_CHECKING:
    from .MainWindow import MainWindow


class _TableColumns:
    NAME = 0
    VERSION = 1
    ID = 2


class ProfileEditorTab(QTableWidget):
    def __init__(self, mainWindow: "MainWindow") -> None:
        super().__init__(0, 3)

        self._mainWindow = mainWindow
        self._profileCollection = ProfileCollection.getInstance()

        self.setColumnHidden(_TableColumns.ID, not Globals.debugMode)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setHorizontalHeaderLabels((
            QCoreApplication.translate("ProfileEditorTab", "Profile Name"),
            QCoreApplication.translate("ProfileEditorTab", "Minecraft Version"),
            QCoreApplication.translate("ProfileEditorTab", "ID"),
        ))
        stretchTableWidgetColumnsSize(self)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.verticalHeader().hide()
        self.setShowGrid(False)

        self._profileCollection.profilesChanged.connect(self._updateProfiles)

        self._updateProfiles()

    def _updateProfiles(self) -> None:
        clearTableWidget(self)

        for row, profile in enumerate(self._profileCollection.getProfileList()):
            nameItem = QTableWidgetItem(profile.name)
            nameItem.setFlags(nameItem.flags() ^ Qt.ItemFlag.ItemIsEditable)

            if profile.useLatestVersion:
                versionItem = QTableWidgetItem(QCoreApplication.translate("ProfileEditorTab", "(Latest version)"))
            elif profile.useLatestSnapshot:
                versionItem = QTableWidgetItem(QCoreApplication.translate("ProfileEditorTab", "(Latest snapshot)"))
            else:
                versionItem = QTableWidgetItem(profile.version)

            versionItem.setFlags(versionItem.flags() ^ Qt.ItemFlag.ItemIsEditable)

            idItem = QTableWidgetItem(profile.id)
            idItem.setFlags(nameItem.flags() ^ Qt.ItemFlag.ItemIsEditable)

            self.insertRow(row)
            self.setItem(row, _TableColumns.NAME, nameItem)
            self.setItem(row, _TableColumns.VERSION, versionItem)
            self.setItem(row, _TableColumns.ID, idItem)

    def _getCurrentProfile(self) -> Profile | None:
        currentID = self.item(self.currentRow(), _TableColumns.ID).text()
        return ProfileCollection.getInstance().getProfileByID(currentID)

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:  # type: ignore
        profile = self._getCurrentProfile()

        if profile is None:
            return

        menu = QMenu(self)

        addProfile = QAction(QCoreApplication.translate("ProfileEditorTab", "Add Profile"), self)
        addProfile.triggered.connect(self._addProfile)
        menu.addAction(addProfile)

        editProfile = QAction(QCoreApplication.translate("ProfileEditorTab", "Edit Profile"), self)
        editProfile.triggered.connect(self._editProfile)
        menu.addAction(editProfile)

        copyProfile = QAction(QCoreApplication.translate("ProfileEditorTab", "Copy Profile"), self)
        copyProfile.triggered.connect(self._copyProfile)
        menu.addAction(copyProfile)

        removeProfile = QAction(QCoreApplication.translate("ProfileEditorTab", "Remove Profile"), self)
        removeProfile.triggered.connect(self._removeProfile)
        menu.addAction(removeProfile)

        openGameFolder = QAction(QCoreApplication.translate("ProfileEditorTab", "Open Game Folder"), self)
        openGameFolder.triggered.connect(lambda: openFile(profile.getGameDirectoryPath()))
        menu.addAction(openGameFolder)

        if canCreateShortcuts():
            createShortcut = QAction(QCoreApplication.translate("ProfileEditorTab", "Create Shortcut"), self)
            createShortcut.triggered.connect(lambda: askCreateShortcut(self._mainWindow, profile))
            menu.addAction(createShortcut)

        menu.popup(event.globalPos())

    def _addProfile(self) -> None:
        self._mainWindow.profileWindow.loadProfile(self._profileCollection.createProfile(QCoreApplication.translate("ProfileEditorTab", "New Profile")), True)
        self._mainWindow.profileWindow.open()

    def _editProfile(self) -> None:
        if (profile := self._getCurrentProfile()) is not None:
            self._mainWindow.profileWindow.loadProfile(profile, False)
            self._mainWindow.profileWindow.open()

    def _copyProfile(self) -> None:
        if (profile := self._getCurrentProfile()) is not None:
            self._mainWindow.profileWindow.loadProfile(profile, True, True)
            self._mainWindow.profileWindow.open()

    def _removeProfile(self) -> None:
        if len(self._profileCollection.getProfileList()) == 1:
            QMessageBox.critical(
                self._mainWindow,
                QCoreApplication.translate("ProfileEditorTab", "Can't delete Profile"),
                QCoreApplication.translate("ProfileEditorTab", "You can't delete all Profiles. At least one Profile must stay.")
            )
        elif (profile := self._getCurrentProfile()) is not None:
            self._profileCollection.removeProfileById(profile.id)
