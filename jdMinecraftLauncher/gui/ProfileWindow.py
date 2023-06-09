from PyQt6.QtWidgets import QDialog, QLabel, QLineEdit, QCheckBox, QComboBox, QPushButton, QFileDialog, QMessageBox, QHBoxLayout, QVBoxLayout, QGridLayout, QLayout
from jdMinecraftLauncher.Functions import saveProfiles, openFile, findJavaRuntimes, isFlatpak
from jdMinecraftLauncher.Shortcut import canCreateShortcuts, askCreateShortcut
from jdMinecraftLauncher.Profile import Profile
from PyQt6.QtCore import QCoreApplication
from PyQt6.QtGui import QIntValidator
from typing import TYPE_CHECKING
import platform
import shutil
import os


if TYPE_CHECKING:
    from jdMinecraftLauncher.gui.MainWindow import MainWindow
    from jdMinecraftLauncher.Environment import Environment
    from jdMinecraftLauncher.Profile import Profile


class ProfileWindow(QDialog):
    def __init__(self, env: "Environment", parent: "MainWindow"):
        super().__init__()
        self.env = env
        self.mainwindow = parent
        self.profileeNameEdit = QLineEdit()
        self.gameDirectoryCheckbox = QCheckBox(QCoreApplication.translate("ProfileWindow", "Game Directory:"))
        self.gameDirectoryBrowseButton = QPushButton(QCoreApplication.translate("ProfileWindow", "Browse"))
        self.gameDirectoryEdit = QLineEdit()
        self.resolutionCheckbox = QCheckBox(QCoreApplication.translate("ProfileWindow", "Resolution:"))
        self.resolutionEditX = QLineEdit()
        self.resolutionLabel = QLabel("x")
        self.resolutionEditY = QLineEdit()
        self.launcherVisibilityCheckbox = QCheckBox(QCoreApplication.translate("ProfileWindow", "Launcher Visibility:"))
        self.launcherVisibilityCombobox = QComboBox()
        self.enableSnapshots = QCheckBox(QCoreApplication.translate("ProfileWindow", 'Enable experimental development Versions ("snapshots")'))
        self.enableBeta = QCheckBox(QCoreApplication.translate("ProfileWindow", 'Allow use of old "Beta" Minecraft Versions (From 2010-2011)'))
        self.enableAlpha = QCheckBox(QCoreApplication.translate("ProfileWindow", 'Allow use of old "Alpha" Minecraft Versions (From 2010)'))
        self.versionSelectCombobox = QComboBox()
        self.executableCheckbox = QCheckBox(QCoreApplication.translate("ProfileWindow", "Executable:"))
        self.executableEdit = QComboBox()
        self.executableButton = QPushButton(QCoreApplication.translate("ProfileWindow", "Browse"))
        self.jvmArgumentsCheckbox = QCheckBox(QCoreApplication.translate("ProfileWindow", "JVM Arguments:"))
        self.jvmArgumentsEdit = QLineEdit()
        self.serverCheckbox = QCheckBox(QCoreApplication.translate("ProfileWindow", "Connect to Server"))
        self.serverLabel = QLabel(QCoreApplication.translate("ProfileWindow", "Server IP:"))
        self.serverEdit = QLineEdit()
        self.portLabel = QLabel(QCoreApplication.translate("ProfileWindow", "Server Port:"))
        self.portEdit = QLineEdit()
        self.demoModeCheckbox = QCheckBox(QCoreApplication.translate("ProfileWindow", "Start in demo mode"))
        self.disableMultiplayerCheckBox = QCheckBox(QCoreApplication.translate("ProfileWindow", "Disable Multiplayer"))
        self.disableChatCheckBox = QCheckBox(QCoreApplication.translate("ProfileWindow", "Disable Chat"))
        self.gameModeCheckBox = QCheckBox(QCoreApplication.translate("ProfileWindow", "Use Gamemode"))
        self.cancelButton = QPushButton(QCoreApplication.translate("ProfileWindow", "Cancel"))
        self.minecraftOptionsCheckBox = QCheckBox(QCoreApplication.translate("ProfileWindow", "Additional Options:"))
        self.minecraftOptionsEdit = QLineEdit()
        self.createShortcutButton = QPushButton(QCoreApplication.translate("ProfileWindow", "Create Shortcut"))
        self.openGameDirectoryButton = QPushButton(QCoreApplication.translate("ProfileWindow", "Open Game Dir"))
        self.saveProfileButton = QPushButton(QCoreApplication.translate("ProfileWindow", "Save Profile"))

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
        self.createShortcutButton.clicked.connect(lambda: askCreateShortcut(self.env, self.profile))
        self.openGameDirectoryButton.clicked.connect(lambda: openFile(self.profile.getGameDirectoryPath()))
        self.saveProfileButton.clicked.connect(self.saveProfile)
        self.executableCheckbox.stateChanged.connect(lambda: self.executableEdit.setEnabled(self.executableCheckbox.isChecked()) or self.executableButton.setEnabled(self.executableCheckbox.isChecked()))
        self.executableButton.clicked.connect(self.browseExecutableClicked)
        self.jvmArgumentsCheckbox.stateChanged.connect(lambda: self.jvmArgumentsEdit.setEnabled(self.jvmArgumentsCheckbox.isChecked()))
        self.serverCheckbox.stateChanged.connect(self.changeServerConnect)
        self.minecraftOptionsCheckBox.stateChanged.connect(lambda: self.minecraftOptionsEdit.setEnabled(self.minecraftOptionsCheckBox.isChecked()))

        gameDirectoryLayout = QHBoxLayout()
        gameDirectoryLayout.addWidget(self.gameDirectoryEdit)
        gameDirectoryLayout.addWidget(self.gameDirectoryBrowseButton)
        gameDirectoryLayout.setSpacing(1)

        self.resolutionLayout = QHBoxLayout()
        self.resolutionLayout.addWidget(self.resolutionEditX)
        self.resolutionLayout.addWidget(self.resolutionLabel)
        self.resolutionLayout.addWidget(self.resolutionEditY)
        
        self.profileInfoLayout = QGridLayout()
        self.profileInfoLayout.addWidget(QLabel(QCoreApplication.translate("ProfileWindow", "Profile Info")), 0, 0)
        self.profileInfoLayout.addWidget(QLabel(QCoreApplication.translate("ProfileWindow", "Profile Name:")), 1, 0)
        self.profileInfoLayout.addWidget(self.profileeNameEdit, 1, 1)
        self.profileInfoLayout.addWidget(self.gameDirectoryCheckbox, 2, 0)
        self.profileInfoLayout.addLayout(gameDirectoryLayout, 2, 1)
        self.profileInfoLayout.addWidget(self.resolutionCheckbox, 3, 0)
        self.profileInfoLayout.addLayout(self.resolutionLayout, 3, 1)
        self.profileInfoLayout.addWidget(self.launcherVisibilityCheckbox, 4, 0)
        self.profileInfoLayout.addWidget(self.launcherVisibilityCombobox, 4, 1)

        self.useVersionLayout = QHBoxLayout()
        self.useVersionLayout.addWidget(QLabel(QCoreApplication.translate("ProfileWindow", "Use Version:")))
        self.useVersionLayout.addWidget(self.versionSelectCombobox)

        javaExecutableLayout = QHBoxLayout()
        javaExecutableLayout.addWidget(self.executableEdit, 2)
        javaExecutableLayout.addWidget(self.executableButton)
        javaExecutableLayout.setSpacing(1)

        self.javaSettingsLayout = QGridLayout()
        self.javaSettingsLayout.addWidget(self.executableCheckbox, 0, 0)
        self.javaSettingsLayout.addLayout(javaExecutableLayout, 0, 1)
        self.javaSettingsLayout.addWidget(self.jvmArgumentsCheckbox, 1, 0)
        self.javaSettingsLayout.addWidget(self.jvmArgumentsEdit, 1, 1)

        self.serverLayout = QGridLayout()
        self.serverLayout.addWidget(self.serverLabel,0,0)
        self.serverLayout.addWidget(self.serverEdit,0,1)
        self.serverLayout.addWidget(self.portLabel,1,0)
        self.serverLayout.addWidget(self.portEdit,1,1)

        minecraftOptionsLayout = QHBoxLayout()
        minecraftOptionsLayout.addWidget(self.minecraftOptionsCheckBox)
        minecraftOptionsLayout.addWidget(self.minecraftOptionsEdit)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.cancelButton)
        buttonLayout.addWidget(self.createShortcutButton)
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(self.openGameDirectoryButton)
        buttonLayout.addWidget(self.saveProfileButton)
        
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addLayout(self.profileInfoLayout)
        self.mainLayout.addWidget(QLabel(QCoreApplication.translate("ProfileWindow", "Version Select")))
        self.mainLayout.addWidget(self.enableSnapshots)
        self.mainLayout.addWidget(self.enableBeta)
        self.mainLayout.addWidget(self.enableAlpha)
        self.mainLayout.addLayout(self.useVersionLayout)
        self.mainLayout.addWidget(QLabel(QCoreApplication.translate("ProfileWindow", "Java Settings (Advanced)")))
        self.mainLayout.addLayout(self.javaSettingsLayout)
        self.mainLayout.addWidget(QLabel(QCoreApplication.translate("ProfileWindow", "Other")))
        self.mainLayout.addWidget(self.serverCheckbox)
        self.mainLayout.addLayout(self.serverLayout)
        self.mainLayout.addWidget(self.demoModeCheckbox)
        self.mainLayout.addWidget(self.disableMultiplayerCheckBox)
        self.mainLayout.addWidget(self.disableChatCheckBox)
        self.mainLayout.addLayout(minecraftOptionsLayout)
        if platform.system() == "Linux":
            self.mainLayout.addWidget(self.gameModeCheckBox)
        self.mainLayout.addLayout(buttonLayout)

        self.mainLayout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        self.setWindowTitle(QCoreApplication.translate("ProfileWindow", "Profile Editor"))
        self.setLayout(self.mainLayout)
        self.selectLatestVersion = True

        if isFlatpak():
            self.gameDirectoryEdit.setReadOnly(True)
            self.executableEdit.lineEdit().setReadOnly(True)

        if not shutil.which("gamemoderun"):
            self.gameModeCheckBox.setEnabled(False)

    def changeCustomResolution(self):
        state = self.resolutionCheckbox.isChecked()
        self.resolutionLabel.setEnabled(state)
        self.resolutionEditX.setEnabled(state)
        self.resolutionEditY.setEnabled(state)

    def changeServerConnect(self):
        state = self.serverCheckbox.isChecked()
        self.serverLabel.setEnabled(state)
        self.serverEdit.setEnabled(state)
        self.portLabel.setEnabled(state)
        self.portEdit.setEnabled(state)

    def browseGameDirectoryClicked(self):
        path = QFileDialog.getExistingDirectory(directory = self.executableEdit.currentText())
        if path != "":
            self.gameDirectoryEdit.setText(path)

    def browseExecutableClicked(self):
        if isFlatpak():
            QMessageBox.information(self, QCoreApplication.translate("ProfileWindow", "Note for Flatpak users"),  QCoreApplication.translate("ProfileWindow", "Please select in the following dialog the directory which contains bin/java"))
            path = QFileDialog.getExistingDirectory()
            if path == "":
                return
            javaPath = os.path.join(path, "bin", "java")
            if os.path.isfile(javaPath):
                self.executableEdit.lineEdit().setText(javaPath)
            else:
                QMessageBox.critical(self, QCoreApplication.translate("ProfileWindow", "Invalid directory"), QCoreApplication.translate("ProfileWindow", "This directory does not contain bin/java"))
        else:
            path = QFileDialog.getOpenFileName(directory = self.executableEdit.currentText())
            if path[0] != "":
                self.executableEdit.lineEdit().setText(path[0])

    def loadProfile(self, profile: "Profile", isNew: bool, copyText: bool = False):
        if isNew:
            if copyText:
                self.profileeNameEdit.setText(QCoreApplication.translate("ProfileWindow", "Copy of {{name}}").replace("{{name}}", profile.name))
            else:
                self.profileeNameEdit.setText(profile.name)
        else:
            self.profileeNameEdit.setText(profile.name)
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

    def saveProfile(self):
        profile = self.profile
        if self.isNew:
            profile = Profile(self.profileeNameEdit.text(), self.env)
        else:
            profile.name = self.profileeNameEdit.text()
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
        self.mainwindow.updateProfileList()
        self.env.profileCollection.save()
        self.close()

    def updateVersionsList(self):
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
