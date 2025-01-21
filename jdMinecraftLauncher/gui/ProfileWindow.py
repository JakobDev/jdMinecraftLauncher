from jdMinecraftLauncher.Functions import openFile, findJavaRuntimes, isFlatpak
from jdMinecraftLauncher.Shortcut import canCreateShortcuts, askCreateShortcut
from PyQt6.QtWidgets import QDialog, QFileDialog, QMessageBox
from ..ui_compiled.ProfileWindow import Ui_ProfileWindow
from jdMinecraftLauncher.Profile import Profile
from PyQt6.QtCore import QCoreApplication
from PyQt6.QtGui import QIntValidator
from typing import TYPE_CHECKING
import platform
import shutil
import os


if TYPE_CHECKING:
    from jdMinecraftLauncher.gui.MainWindow.MainWindow import MainWindow
    from jdMinecraftLauncher.Environment import Environment


class ProfileWindow(QDialog, Ui_ProfileWindow):
    def __init__(self, env: "Environment", parent: "MainWindow") -> None:
        super().__init__(parent)

        self.setupUi(self)

        self.env = env
        self.mainWindow = parent

        self.resolutionEditX.setValidator(QIntValidator(self.resolutionEditX))
        self.resolutionEditY.setValidator(QIntValidator(self.resolutionEditY))

        self.launcherVisibilityCombobox.addItem(QCoreApplication.translate("ProfileWindow", "Hide Launcher and re-open when game closes"))
        self.launcherVisibilityCombobox.addItem(QCoreApplication.translate("ProfileWindow", "Close Launcher when Game starts"))
        self.launcherVisibilityCombobox.addItem(QCoreApplication.translate("ProfileWindow", "Keep the Launcher open"))

        self.executableEdit.setEditable(True)
        self.executableEdit.addItems(findJavaRuntimes())

        self.gameDirectoryCheckbox.stateChanged.connect(lambda: self.gameDirectoryEdit.setEnabled(self.gameDirectoryCheckbox.isChecked()) or self.gameDirectoryBrowseButton.setEnabled(self.gameDirectoryCheckbox.isChecked()))
        self.gameDirectoryBrowseButton.clicked.connect(self.browseGameDirectoryClicked)
        self.resolutionCheckbox.stateChanged.connect(self.changeCustomResolution)
        self.launcherVisibilityCheckbox.stateChanged.connect(lambda: self.launcherVisibilityCombobox.setEnabled(self.launcherVisibilityCheckbox.isChecked()))
        self.enableSnapshots.stateChanged.connect(self.updateVersionsList)
        self.enableBeta.stateChanged.connect(self.updateVersionsList)
        self.enableAlpha.stateChanged.connect(self.updateVersionsList)
        self.cancelButton.clicked.connect(self.close)
        self.createShortcutButton.clicked.connect(lambda: askCreateShortcut(self.env, self, self.profile))  # type: ignore
        self.openGameDirectoryButton.clicked.connect(lambda: openFile(self.profile.getGameDirectoryPath()))  # type: ignore
        self.saveProfileButton.clicked.connect(self.saveProfile)
        self.executableCheckbox.stateChanged.connect(lambda: self.executableEdit.setEnabled(self.executableCheckbox.isChecked()) or self.executableButton.setEnabled(self.executableCheckbox.isChecked()))
        self.executableButton.clicked.connect(self.browseExecutableClicked)
        self.jvmArgumentsCheckbox.stateChanged.connect(lambda: self.jvmArgumentsEdit.setEnabled(self.jvmArgumentsCheckbox.isChecked()))
        self.serverCheckbox.stateChanged.connect(self.changeServerConnect)
        self.minecraftOptionsCheckBox.stateChanged.connect(lambda: self.minecraftOptionsEdit.setEnabled(self.minecraftOptionsCheckBox.isChecked()))

        self.selectLatestVersion = True

        if platform.system() != "Linux":
            self.gameModeCheckBox.setVisible(False)

        if isFlatpak():
            self.gameDirectoryEdit.setReadOnly(True)
            self.executableEdit.lineEdit().setReadOnly(True)

        if not shutil.which("gamemoderun"):
            self.gameModeCheckBox.setEnabled(False)

        self.resize(self.minimumSize())

    def changeCustomResolution(self) -> None:
        state = self.resolutionCheckbox.isChecked()
        self.resolutionLabel.setEnabled(state)
        self.resolutionEditX.setEnabled(state)
        self.resolutionEditY.setEnabled(state)

    def changeServerConnect(self) -> None:
        state = self.serverCheckbox.isChecked()
        self.serverLabel.setEnabled(state)
        self.serverEdit.setEnabled(state)
        self.portLabel.setEnabled(state)
        self.portEdit.setEnabled(state)

    def browseGameDirectoryClicked(self) -> None:
        path = QFileDialog.getExistingDirectory(directory=self.executableEdit.currentText())
        if path != "":
            self.gameDirectoryEdit.setText(path)

    def browseExecutableClicked(self) -> None:
        if isFlatpak():
            QMessageBox.information(self, QCoreApplication.translate("ProfileWindow", "Note for Flatpak users"), QCoreApplication.translate("ProfileWindow", "Please select in the following dialog the directory which contains bin/java"))
            path = QFileDialog.getExistingDirectory()
            if path == "":
                return
            javaPath = os.path.join(path, "bin", "java")
            if os.path.isfile(javaPath):
                self.executableEdit.lineEdit().setText(javaPath)
            else:
                QMessageBox.critical(self, QCoreApplication.translate("ProfileWindow", "Invalid directory"), QCoreApplication.translate("ProfileWindow", "This directory does not contain bin/java"))
        else:
            path = QFileDialog.getOpenFileName(directory=self.executableEdit.currentText())[0]
            if path != "":
                self.executableEdit.lineEdit().setText(path[0])

    def loadProfile(self, profile: "Profile", isNew: bool, copyText: bool = False) -> None:
        if isNew:
            if copyText:
                self.profileNameEdit.setText(QCoreApplication.translate("ProfileWindow", "Copy of {{name}}").replace("{{name}}", profile.name))
            else:
                self.profileNameEdit.setText(profile.name)
        else:
            self.profileNameEdit.setText(profile.name)

        self.gameDirectoryCheckbox.setChecked(profile.customGameDirectory)
        self.gameDirectoryEdit.setEnabled(profile.customGameDirectory)
        self.gameDirectoryBrowseButton.setEnabled(profile.customGameDirectory)
        self.gameDirectoryEdit.setText(profile.gameDirectoryPath)
        self.resolutionCheckbox.setChecked(profile.customResolution)
        self.resolutionEditX.setText(profile.resolutionX)
        self.resolutionEditY.setText(profile.resolutionY)
        self.launcherVisibilityCheckbox.setChecked(profile.customLauncherVisibility)
        self.launcherVisibilityCombobox.setEnabled(profile.customLauncherVisibility)
        self.launcherVisibilityCombobox.setCurrentIndex(profile.launcherVisibility)
        self.enableSnapshots.setChecked(profile.enableSnapshots)
        self.enableBeta.setChecked(profile.enableBeta)
        self.enableAlpha.setChecked(profile.enableAlpha)
        self.selectLatestVersion = profile.useLatestVersion
        self.selectLatestSnapshot = profile.useLatestSnapshot
        self.selectedVersion = profile.version
        self.executableCheckbox.setChecked(profile.customExecutable)
        self.executableEdit.setEnabled(profile.customExecutable)
        self.executableButton.setEnabled(profile.customExecutable)
        self.executableEdit.lineEdit().setText(profile.executable)
        self.jvmArgumentsCheckbox.setChecked(profile.customArguments)
        self.jvmArgumentsEdit.setEnabled(profile.customArguments)
        self.jvmArgumentsEdit.setText(profile.arguments)
        self.serverCheckbox.setChecked(profile.serverConnect)
        self.serverEdit.setText(profile.serverIP)
        self.portEdit.setText(profile.serverPort)
        self.demoModeCheckbox.setChecked(profile.demoMode)
        self.disableMultiplayerCheckBox.setChecked(profile.disableMultiplayer)
        self.disableChatCheckBox.setChecked(profile.disableChat)
        self.minecraftOptionsCheckBox.setChecked(profile.hasMinecraftOptions)
        self.minecraftOptionsEdit.setEnabled(profile.hasMinecraftOptions)
        self.minecraftOptionsEdit.setText(profile.minecraftOptions)
        self.gameModeCheckBox.setChecked(profile.useGameMode)
        self.changeCustomResolution()
        self.changeServerConnect()
        self.updateVersionsList()

        self.createShortcutButton.setVisible(not isNew and canCreateShortcuts())

        self.profile = profile
        self.isNew = isNew

    def saveProfile(self) -> None:
        profile = self.profile

        if self.isNew:
            profile = Profile(self.profileNameEdit.text(), self.env)
        else:
            profile.name = self.profileNameEdit.text()

        profile.customGameDirectory = self.gameDirectoryCheckbox.isChecked()
        profile.gameDirectoryPath = self.gameDirectoryEdit.text()
        profile.customResolution = self.resolutionCheckbox.isChecked()
        profile.resolutionX = self.resolutionEditX.text()
        profile.resolutionY = self.resolutionEditY.text()
        profile.customLauncherVisibility = self.launcherVisibilityCheckbox.isChecked()
        profile.launcherVisibility = self.launcherVisibilityCombobox.currentIndex()
        profile.enableSnapshots = self.enableSnapshots.isChecked()
        profile.enableBeta = self.enableBeta.isChecked()
        profile.enableAlpha = self.enableAlpha.isChecked()
        profile.customExecutable = self.executableCheckbox.isChecked()
        profile.executable = self.executableEdit.currentText()
        profile.customArguments = self.jvmArgumentsCheckbox.isChecked()
        profile.serverConnect = self.serverCheckbox.isChecked()
        profile.arguments = self.jvmArgumentsEdit.text()
        profile.serverIP = self.serverEdit.text()
        profile.serverPort = self.portEdit.text()
        profile.demoMode = self.demoModeCheckbox.isChecked()
        profile.disableMultiplayer = self.disableMultiplayerCheckBox.isChecked()
        profile.disableChat = self.disableChatCheckBox.isChecked()
        profile.hasMinecraftOptions = self.minecraftOptionsCheckBox.isChecked()
        profile.minecraftOptions = self.minecraftOptionsEdit.text().strip()
        profile.useGameMode = self.gameModeCheckBox.isChecked()
        version = self.versionSelectCombobox.currentData()

        if version == "latestRelease":
            profile.useLatestVersion = True
            profile.useLatestSnapshot = False
        elif version == "latestSnapshot":
            profile.useLatestSnapshot = True
            profile.useLatestVersion = False
        else:
            profile.useLatestVersion = False
            profile.useLatestSnapshot = False
            profile.version = version

        if self.isNew:
            self.env.profileCollection.profileList.append(profile)
            self.env.profileCollection.selectedProfile = profile.id

        self.mainWindow.updateProfileList()
        self.env.profileCollection.save()
        self.close()

    def updateVersionsList(self) -> None:
        self.versionSelectCombobox.clear()
        self.versionSelectCombobox.addItem(QCoreApplication.translate("ProfileWindow", "Use latest Version"), "latestRelease")

        if self.enableSnapshots.isChecked():
            self.versionSelectCombobox.addItem(QCoreApplication.translate("ProfileWindow", "Use latest Snapshot"), "latestSnapshot")

        for i in self.env.versions["versions"]:
            if i["type"] == "release":
                self.versionSelectCombobox.addItem("release " + i["id"], i["id"])
            elif i["type"] == "snapshot" and self.enableSnapshots.isChecked():
                self.versionSelectCombobox.addItem("snapshot " + i["id"], i["id"])
            elif i["type"] == "old_beta" and self.enableBeta.isChecked():
                self.versionSelectCombobox.addItem("old_beta " + i["id"], i["id"])
            elif i["type"] == "old_alpha" and self.enableAlpha.isChecked():
                self.versionSelectCombobox.addItem("old_alpha " + i["id"], i["id"])

        if self.selectLatestVersion:
            self.versionSelectCombobox.setCurrentIndex(0)
        elif self.selectLatestSnapshot and self.enableSnapshots.isChecked():
            self.versionSelectCombobox.setCurrentIndex(1)
        else:
            for i in range(self.versionSelectCombobox.count()):
                if self.versionSelectCombobox.itemText(i).split(" ", 1)[1] == self.selectedVersion:
                    self.versionSelectCombobox.setCurrentIndex(i)
