from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QCheckBox, QComboBox, QPushButton, QFileDialog, QMessageBox, QHBoxLayout, QVBoxLayout, QGridLayout, QLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIntValidator
from jdMinecraftLauncher.Profile import Profile
from jdMinecraftLauncher.Functions import saveProfiles, openFile, findJavaRuntimes, isFlatpak
import platform
import shutil
import os


class ProfileWindow(QWidget):
    def __init__(self, enviroment, parrent):
        super().__init__()
        self.env = enviroment
        self.mainwindow = parrent
        self.profileNameEdit = QLineEdit()
        self.gameDirectoryCheckbox = QCheckBox(self.env.translate("profilewindow,checkbox.gameDirectory"))
        self.gameDirectoryBrowseButton = QPushButton(self.env.translate("profilewindow.button.browse"))
        self.gameDirectoryEdit = QLineEdit()
        self.resolutionCheckbox = QCheckBox(self.env.translate("profilewindow.checkbox.resolution"))
        self.resolutionEditX = QLineEdit()
        self.resolutionLabel = QLabel("x")
        self.resolutionEditY = QLineEdit()
        self.launcherVisibilityCheckbox = QCheckBox(self.env.translate("profilewindow.checkbox.launcherVisibility"))
        self.launcherVisibilityCombobox = QComboBox()
        self.enableSnapshots = QCheckBox(self.env.translate("profilewindow.checkbox.enableSnapshots"))
        self.enableBeta = QCheckBox(self.env.translate("profilewindow.checkbox.enableBeta"))
        self.enableAlpha = QCheckBox(self.env.translate("profilewindow.checkbox.enableAlpha"))
        self.versionSelectCombobox = QComboBox()
        self.executableCheckbox = QCheckBox(self.env.translate("profilewindow.checkbox.executable"))
        self.executableEdit = QComboBox()
        self.executableButton = QPushButton(self.env.translate("profilewindow.button.browse"))
        self.jvmArgumentsCheckbox = QCheckBox(self.env.translate("profilewindow.checkbox.jvmArguments"))
        self.jvmArgumentsEdit = QLineEdit()
        self.serverCheckbox = QCheckBox(self.env.translate("profilewindow.checkbox.serverConnect"))
        self.serverLabel = QLabel(self.env.translate("profilewindow.label.ip"))
        self.serverEdit = QLineEdit()
        self.portLabel = QLabel(self.env.translate("profilewindow.label.port"))
        self.portEdit = QLineEdit()
        self.demoModeCheckbox = QCheckBox(self.env.translate("profilewindow.checkbox.demoMode"))
        self.gameModeCheckBox = QCheckBox(self.env.translate("profilewindow.checkbox.gameMode"))
        self.cancelButton = QPushButton(self.env.translate("profilewindow.button.cancel"))
        self.openGameDirectoryButton = QPushButton(self.env.translate("profilewindow.button.openGameDir"))
        self.saveProfileButton = QPushButton(self.env.translate("profilewindow.button.saveProfile"))

        self.resolutionEditX.setValidator(QIntValidator(self.resolutionEditX))
        self.resolutionEditY.setValidator(QIntValidator(self.resolutionEditY))

        self.launcherVisibilityCombobox.addItem(self.env.translate("profilewindow.launcherVisibility.hide"))
        self.launcherVisibilityCombobox.addItem(self.env.translate("profilewindow.launcherVisibility.close"))
        self.launcherVisibilityCombobox.addItem(self.env.translate("profilewindow.launcherVisibility.keep"))

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
        self.openGameDirectoryButton.clicked.connect(lambda: openFile(self.profil.getGameDirectoryPath()))
        self.saveProfileButton.clicked.connect(self.saveProfile)
        self.executableCheckbox.stateChanged.connect(lambda: self.executableEdit.setEnabled(self.executableCheckbox.isChecked()) or self.executableButton.setEnabled(self.executableCheckbox.isChecked()))
        self.executableButton.clicked.connect(self.browseExecutableClicked)
        self.jvmArgumentsCheckbox.stateChanged.connect(lambda: self.jvmArgumentsEdit.setEnabled(self.jvmArgumentsCheckbox.isChecked()))
        self.serverCheckbox.stateChanged.connect(self.changeServerConnect)

        gameDirectoryLayout = QHBoxLayout()
        gameDirectoryLayout.addWidget(self.gameDirectoryEdit)
        gameDirectoryLayout.addWidget(self.gameDirectoryBrowseButton)
        gameDirectoryLayout.setSpacing(1)

        self.resolutionLayout = QHBoxLayout()
        self.resolutionLayout.addWidget(self.resolutionEditX)
        self.resolutionLayout.addWidget(self.resolutionLabel)
        self.resolutionLayout.addWidget(self.resolutionEditY)
        
        self.profileInfoLayout = QGridLayout()
        self.profileInfoLayout.addWidget(QLabel(self.env.translate("profilewindow.label.profileInfo")),0,0)
        self.profileInfoLayout.addWidget(QLabel(self.env.translate("profilewindow.label.profileName")),1,0)
        self.profileInfoLayout.addWidget(self.profileNameEdit,1,1)
        self.profileInfoLayout.addWidget(self.gameDirectoryCheckbox,2,0)
        self.profileInfoLayout.addLayout(gameDirectoryLayout, 2, 1)
        self.profileInfoLayout.addWidget(self.resolutionCheckbox,3,0)
        self.profileInfoLayout.addLayout(self.resolutionLayout,3,1)
        self.profileInfoLayout.addWidget(self.launcherVisibilityCheckbox,4,0)
        self.profileInfoLayout.addWidget(self.launcherVisibilityCombobox,4,1)

        self.useVersionLayout = QHBoxLayout()
        self.useVersionLayout.addWidget(QLabel(self.env.translate("profilewindow.label.useVersion")))
        self.useVersionLayout.addWidget(self.versionSelectCombobox)

        javaExecutableLayout = QHBoxLayout()
        javaExecutableLayout.addWidget(self.executableEdit, 2)
        javaExecutableLayout.addWidget(self.executableButton)
        javaExecutableLayout.setSpacing(1)

        self.javaSettingsLayout = QGridLayout()
        self.javaSettingsLayout.addWidget(self.executableCheckbox,0,0)
        self.javaSettingsLayout.addLayout(javaExecutableLayout, 0, 1)
        self.javaSettingsLayout.addWidget(self.jvmArgumentsCheckbox,1,0)
        self.javaSettingsLayout.addWidget(self.jvmArgumentsEdit,1,1)

        self.serverLayout = QGridLayout()
        self.serverLayout.addWidget(self.serverLabel,0,0)
        self.serverLayout.addWidget(self.serverEdit,0,1)
        self.serverLayout.addWidget(self.portLabel,1,0)
        self.serverLayout.addWidget(self.portEdit,1,1)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.addWidget(self.cancelButton)
        self.buttonLayout.addStretch(1)
        self.buttonLayout.addWidget(self.openGameDirectoryButton)
        self.buttonLayout.addWidget(self.saveProfileButton)
        
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addLayout(self.profileInfoLayout)
        self.mainLayout.addWidget(QLabel(self.env.translate("profilewindow.label.versionSelect")))
        self.mainLayout.addWidget(self.enableSnapshots)
        self.mainLayout.addWidget(self.enableBeta)
        self.mainLayout.addWidget(self.enableAlpha)
        self.mainLayout.addLayout(self.useVersionLayout)
        self.mainLayout.addWidget(QLabel(self.env.translate("profilewindow.javaSettings")))
        self.mainLayout.addLayout(self.javaSettingsLayout)
        self.mainLayout.addWidget(QLabel(self.env.translate("profilewindow.checkbox.other")))
        self.mainLayout.addWidget(self.serverCheckbox)
        self.mainLayout.addLayout(self.serverLayout)
        self.mainLayout.addWidget(self.demoModeCheckbox)
        if platform.system() == "Linux":
            self.mainLayout.addWidget(self.gameModeCheckBox)
        self.mainLayout.addLayout(self.buttonLayout)

        self.mainLayout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        self.setWindowTitle(self.env.translate("profilewindow.title"))
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
            QMessageBox.information(self, self.env.translate("profilewindow.executableFlatpakInfo.title"), self.env.translate("profilewindow.executableFlatpakInfo.text"))
            path = QFileDialog.getExistingDirectory()
            if path == "":
                return
            javaPath = os.path.join(path, "bin", "java")
            if os.path.isfile(javaPath):
                self.executableEdit.lineEdit().setText(javaPath)
            else:
                QMessageBox.critical(self, self.env.translate("profilewindow.executableFlatpakWrongDir.title"), self.env.translate("profilewindow.executableFlatpakWrongDir.text"))
        else:
            path = QFileDialog.getOpenFileName(directory = self.executableEdit.currentText())
            if path[0] != "":
                self.executableEdit.lineEdit().setText(path[0])

    def loadProfile(self, profile, isNew, copyText=False):
        if isNew:
            if copyText:
                self.profileNameEdit.setText(self.env.translate("profilewindow.copyOf") % profile.name)
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
        self.gameModeCheckBox.setChecked(profile.useGameMode)
        self.changeCustomResolution()
        self.changeServerConnect()
        self.updateVersionsList()
        self.profil = profile
        self.isNew = isNew

    def saveProfile(self):
        profile = self.profil
        if self.isNew:
            profile = Profile(self.profileNameEdit.text(),self.env)
        else:
            profile.name = self.profileNameEdit.text()
        profile.customGameDirectory = self.toBoolean(self.gameDirectoryCheckbox.isChecked())
        profile.gameDirectoryPath = self.gameDirectoryEdit.text()
        profile.customResolution = self.toBoolean(self.resolutionCheckbox.isChecked())
        profile.resolutionX = self.resolutionEditX.text()
        profile.resolutionY = self.resolutionEditY.text()
        profile.customLauncherVisibility = self.toBoolean(self.launcherVisibilityCheckbox.isChecked())
        profile.launcherVisibility = self.launcherVisibilityCombobox.currentIndex()
        profile.enableSnapshots = self.toBoolean(self.enableSnapshots.isChecked())
        profile.enableBeta = self.toBoolean(self.enableBeta.isChecked())
        profile.enableAlpha = self.toBoolean(self.enableAlpha.isChecked())
        profile.customExecutable = self.toBoolean(self.executableCheckbox.isChecked())
        profile.executable = self.executableEdit.currentText()
        profile.customArguments = self.toBoolean(self.jvmArgumentsCheckbox.isChecked())
        profile.serverConnect = self.toBoolean(self.serverCheckbox.isChecked())
        profile.arguments = self.jvmArgumentsEdit.text()
        profile.serverIP = self.serverEdit.text()
        profile.serverPort = self.portEdit.text()
        profile.demoMode = bool(self.demoModeCheckbox.isChecked())
        profile.useGameMode = self.gameModeCheckBox.isChecked()
        version = self.versionSelectCombobox.currentText()
        if version == self.env.translate("profilewindow.useLatestVersion"):
            profile.useLatestVersion = True
            profile.useLatestSnapshot = False
        elif version == self.env.translate("profilewindow.useLatestSnapshot"):
            profile.useLatestSnapshot = True
            profile.useLatestVersion = False
        else:
            profile.useLatestVersion = False
            profile.useLatestSnapshot = False
            profile.version = version
        if self.isNew:
            self.env.profiles.append(profile)
            self.env.selectedProfile = len(self.env.profiles) - 1
        self.mainwindow.updateProfilList()
        saveProfiles(self.env)
        self.close()

    def updateVersionsList(self):
        self.versionSelectCombobox.clear()
        self.versionSelectCombobox.addItem(self.env.translate("profilewindow.useLatestVersion"))
        if self.enableSnapshots.isChecked():
            self.versionSelectCombobox.addItem(self.env.translate("profilewindoe.useLatestSnapshot"))
        for i in self.env.versions["versions"]:
            if i["type"] == "release":
                self.versionSelectCombobox.addItem("release " + i["id"])
            elif i["type"] == "snapshot" and self.enableSnapshots.isChecked():
                self.versionSelectCombobox.addItem("snapshot " + i["id"])
            elif i["type"] == "old_beta" and self.enableBeta.isChecked():
                self.versionSelectCombobox.addItem("old_beta " + i["id"])
            elif i["type"] == "old_alpha" and self.enableAlpha.isChecked():
                self.versionSelectCombobox.addItem("old_alpha " + i["id"])
        if self.selectLatestVersion:
            self.versionSelectCombobox.setCurrentIndex(0)
        elif self.selectLatestSnapshot and self.enableSnapshots.isChecked():
            self.versionSelectCombobox.setCurrentIndex(1)
        else:
            for i in range(self.versionSelectCombobox.count()):
                if self.versionSelectCombobox.itemText(i) == self.selectedVersion:
                    self.versionSelectCombobox.setCurrentIndex(i)

    def toBoolean(self, value):
        if value == Qt.CheckState.Checked:
            return True
        elif value == Qt.CheckState.Unchecked:
            return False
        else:
            return value
