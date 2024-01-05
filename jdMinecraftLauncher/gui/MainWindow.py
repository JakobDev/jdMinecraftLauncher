from PyQt6.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout, QGridLayout, QPlainTextEdit, QTabWidget, QAbstractItemView, QHeaderView, QPushButton, QComboBox, QProgressBar, QLabel, QCheckBox, QMenu, QLineEdit, QSizePolicy, QMessageBox
from PyQt6.QtCore import QUrl, QLocale, Qt, QProcess, QCoreApplication, QEvent
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile
from PyQt6.QtGui import QCursor, QAction, QIcon, QContextMenuEvent, QCloseEvent
from jdMinecraftLauncher.gui.ProfileWindow import ProfileWindow
from jdMinecraftLauncher.Profile import Profile
from jdMinecraftLauncher.Shortcut import canCreateShortcuts, askCreateShortcut
from jdMinecraftLauncher.Functions import openFile, getAccountDict
from jdMinecraftLauncher.InstallThread import InstallThread
from jdMinecraftLauncher.RunMinecraft import getMinecraftCommand
from jdMinecraftLauncher.Environment import Environment
from jdMinecraftLauncher.Languages import getLanguageNames
from jdMinecraftLauncher.utils.WindowIconProgress import createWindowIconProgress
import minecraft_launcher_lib
from typing import List
import urllib.parse
import webbrowser
import platform
import tempfile
import random
import shutil
import json
import sys
import os


class ProfileEditorTab(QTableWidget):
    def __init__(self, env: Environment, mainwindow: "MainWindow"):
        super().__init__(0,2)
        self.env = env
        self.mainWindow = mainwindow
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setHorizontalHeaderLabels((QCoreApplication.translate("MainWindow", "Profile Name"), QCoreApplication.translate("MainWindow", "Minecraft Version")))
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.verticalHeader().hide()
        self.setShowGrid(False)
        self.updateProfiles()

    def updateProfiles(self):
        while self.rowCount() > 0:
            self.removeRow(0)
        count = 0
        for i in self.env.profileCollection.profileList:
            nameItem = QTableWidgetItem(i.name)
            nameItem.setFlags(nameItem.flags() ^ Qt.ItemFlag.ItemIsEditable)
            if i.useLatestVersion:
                versionItem = QTableWidgetItem(QCoreApplication.translate("MainWindow", "(Latest version)"))
            elif i.useLatestSnapshot:
                versionItem = QTableWidgetItem(QCoreApplication.translate("MainWindow", "(Latest snapshot)"))
            else:
                versionItem = QTableWidgetItem(i.version)
            versionItem.setFlags(versionItem.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.insertRow(count)
            self.setItem(count, 0, nameItem) 
            self.setItem(count, 1, versionItem) 
            count += 1

    def contextMenuEvent(self, event: QContextMenuEvent):
        self.menu = QMenu(self)

        addProfile = QAction(QCoreApplication.translate("MainWindow", "Add Profile"), self)
        addProfile.triggered.connect(self.addProfile)
        self.menu.addAction(addProfile)
    
        editProfile = QAction(QCoreApplication.translate("MainWindow", "Edit Profile"), self)
        editProfile.triggered.connect(self.editProfile)
        self.menu.addAction(editProfile)

        copyProfile = QAction(QCoreApplication.translate("MainWindow", "Copy Profile"), self)
        copyProfile.triggered.connect(self.copyProfile)
        self.menu.addAction(copyProfile)

        removeProfile = QAction(QCoreApplication.translate("MainWindow", "Remove Profile"), self)
        removeProfile.triggered.connect(self.removeProfile)
        self.menu.addAction(removeProfile)

        openGameFolder = QAction(QCoreApplication.translate("MainWindow", "Open Game Folder"), self)
        openGameFolder.triggered.connect(lambda: openFile(self.env.profileCollection.profileList[self.currentRow()].getGameDirectoryPath()))
        self.menu.addAction(openGameFolder)

        if canCreateShortcuts():
            createShortcut = QAction(QCoreApplication.translate("MainWindow", "Create Shortcut"), self)
            createShortcut.triggered.connect(lambda: askCreateShortcut(self.env, self.env.profileCollection.profileList[self.currentRow()]))
            self.menu.addAction(createShortcut)

        self.menu.popup(QCursor.pos())

    def addProfile(self):
        self.mainWindow.profileWindow.loadProfile(Profile(QCoreApplication.translate("MainWindow", "New Profile"), self.env), True)
        self.mainWindow.profileWindow.exec()

    def editProfile(self):
        self.mainWindow.profileWindow.loadProfile(self.env.profileCollection.profileList[self.currentRow()],False)
        self.mainWindow.profileWindow.exec()

    def copyProfile(self):
        self.mainWindow.profileWindow.loadProfile(self.env.profileCollection.profileList[self.currentRow()], True, True)
        self.mainWindow.profileWindow.exec()

    def removeProfile(self):
        if len(self.env.profileCollection.profileList) == 1:
            QMessageBox.critical(self.mainWindow, QCoreApplication.translate("MainWindow", "Can't delete Profile"), QCoreApplication.translate("MainWindow", "You can't delete all Profiles. At least one Profile must stay."))
        else:
            del self.env.profileCollection.profileList[self.currentRow()]
            self.env.selectedProfile = self.env.profileCollection.profileList[0].id
            self.mainWindow.updateProfileList()

class VersionEditorTab(QTableWidget):
    def __init__(self, env: Environment):
        super().__init__(0, 2)
        self.env = env

        self.uninstallVersion = QAction(QCoreApplication.translate("MainWindow", "Uninstall Version"), self)
        self.uninstallVersion.triggered.connect(self.uninstallVersionClicked)

        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setHorizontalHeaderLabels((QCoreApplication.translate("MainWindow", "Minecraft Version"), QCoreApplication.translate("MainWindow", "Version Type")))
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.verticalHeader().hide()
        self.setShowGrid(False)
        self.updateVersions()

    def updateVersions(self):
        if len(self.env.installedVersion) == 0:
            self.uninstallVersion.setEnabled(False)
        else:
            self.uninstallVersion.setEnabled(True)
        while self.rowCount() > 0:
            self.removeRow(0)
        count = 0
        for i in self.env.installedVersion:
            idItem = QTableWidgetItem(i["id"])
            idItem.setFlags(idItem.flags() ^ Qt.ItemFlag.ItemIsEditable)
            typeItem = QTableWidgetItem(i["type"])
            typeItem.setFlags(typeItem.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.insertRow(count)
            self.setItem(count, 0, idItem) 
            self.setItem(count, 1, typeItem) 
            count += 1

    def contextMenuEvent(self, event: QContextMenuEvent):
        self.menu = QMenu(self)

        self.menu.addAction(self.uninstallVersion)

        self.menu.popup(QCursor.pos())

    def uninstallVersionClicked(self):
        shutil.rmtree(os.path.join(self.env.minecraftDir, "versions", self.env.installedVersion[self.currentRow()]["id"]))
        del self.env.installedVersion[self.currentRow()]
        self.updateVersions()

class OptionsTab(QWidget):
    def __init__(self, env: Environment, parent: "MainWindow"):
        super().__init__()
        self.env = env
        self._parent = parent

        self.languageComboBox = QComboBox()
        self.urlEdit = QLineEdit()
        self.allowMultiLaunchCheckBox = QCheckBox(QCoreApplication.translate("MainWindow", "Allow starting multiple instances (not recommended)"))
        self.extractNativesCheckBox = QCheckBox(QCoreApplication.translate("MainWindow", "Unpack natives separately for each instance"))
        self.windowIconProgressCheckBox = QCheckBox(QCoreApplication.translate("MainWindow", "Display installation progress in the window icon"))

        languageNames = getLanguageNames()
        self.languageComboBox.addItem(languageNames.get("en", "en"), "en")
        for i in os.listdir(os.path.join(env.currentDir,"translations")):
            if not i.endswith(".qm"):
                continue

            lang = i.removeprefix("jdMinecraftLauncher_").removesuffix(".qm")
            self.languageComboBox.addItem(languageNames.get(lang, lang), lang)
        self.languageComboBox.model().sort(0, Qt.SortOrder.AscendingOrder)
        self.languageComboBox.insertItem(0, QCoreApplication.translate("MainWindow", "Use System Language"), "default")

        for i in range(self.languageComboBox.count()):
            if self.languageComboBox.itemData(i) == env.settings.get("language"):
                self.languageComboBox.setCurrentIndex(i)

        self.urlEdit.setText(env.settings.get("newsURL"))
        self.allowMultiLaunchCheckBox.setChecked(self.env.settings.get("enableMultiLaunch"))
        self.extractNativesCheckBox.setChecked(self.env.settings.get("extractNatives"))
        self.windowIconProgressCheckBox.setChecked(self.env.settings.get("windowIconProgress"))

        self.windowIconProgressCheckBox.setVisible(parent.windowIconProgress.isSupported())

        self.allowMultiLaunchCheckBox.stateChanged.connect(self.multiLaunchCheckBoxChanged)
        self.extractNativesCheckBox.stateChanged.connect(self.extractNativesCheckBoxChanged)
        self.windowIconProgressCheckBox.stateChanged.connect(self.windowIconProgressCheckBoxChanged)

        gridLayout = QGridLayout()
        gridLayout.addWidget(QLabel(QCoreApplication.translate("MainWindow", "Language:")), 0, 0)
        gridLayout.addWidget(self.languageComboBox,0,1)
        gridLayout.addWidget(QLabel(QCoreApplication.translate("MainWindow", "News URL:")),1,0)
        gridLayout.addWidget(self.urlEdit,1,1)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(gridLayout)
        mainLayout.addWidget(self.allowMultiLaunchCheckBox)
        mainLayout.addWidget(self.extractNativesCheckBox)
        mainLayout.addWidget(self.windowIconProgressCheckBox)
        mainLayout.addStretch(1)
        
        self.setLayout(mainLayout)

    def multiLaunchCheckBoxChanged(self):
        self.env.settings.set("enableMultiLaunch", self.allowMultiLaunchCheckBox.isChecked())

    def extractNativesCheckBoxChanged(self):
        self.env.settings.set("extractNatives", self.extractNativesCheckBox.isChecked())

    def windowIconProgressCheckBoxChanged(self) -> None:
        checked = self.windowIconProgressCheckBox.isChecked()
        self.env.settings.set("windowIconProgress", checked)
        if not checked:
            self._parent.windowIconProgress.hide()


class ForgeTab(QTableWidget):
    def __init__(self, env: Environment, mainWindow: "MainWindow"):
        self.env = env
        self.mainWindow = mainWindow
        super().__init__(0,2)

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

            installButton = QPushButton(QCoreApplication.translate("MainWindow", "Install"))

            installButton.clicked.connect(self.installButtonClicked)

            self.insertRow(count)
            self.setItem(count, 0, versionItem)
            self.setCellWidget(count, 1, installButton)

            count += 1

    def installForgeVersion(self, forgeVersion: str):
        self.mainWindow.installThread.setupForgeInstallation(forgeVersion)
        self.mainWindow.installThread.start()

        self.mainWindow.setInstallButtonsEnabled(False)

    def installButtonClicked(self):
        for i in range(self.rowCount()):
            if self.cellWidget(i, 1) == self.sender():
                self.installForgeVersion(self.item(i, 0).text())
                return

    def setButtonsEnabled(self, enabled: bool):
        for i in range(self.rowCount()):
            self.cellWidget(i, 1).setEnabled(enabled)


class FabricTab(QTableWidget):
    def __init__(self, env: Environment, mainWindow: "MainWindow"):
        self.env = env
        self.mainWindow = mainWindow
        super().__init__(0,2)

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

            installButton = QPushButton(QCoreApplication.translate("MainWindow", "Install"))

            installButton.clicked.connect(self.installButtonClicked)

            self.insertRow(count)
            self.setItem(count, 0, versionItem)
            self.setCellWidget(count, 1, installButton)

            count += 1

    def installFabricVersion(self, fabricVersion: str):
        self.mainWindow.installThread.setupFabricInstallation(fabricVersion)
        self.mainWindow.installThread.start()

        self.mainWindow.setInstallButtonsEnabled(False)

    def installButtonClicked(self):
        for i in range(self.rowCount()):
            if self.cellWidget(i, 1) == self.sender():
                self.installFabricVersion(self.item(i, 0).text())
                return

    def setButtonsEnabled(self, enabled: bool):
        for i in range(self.rowCount()):
            self.cellWidget(i, 1).setEnabled(enabled)


class SwitchAccountButton(QPushButton):
    def __init__(self, text: str, env: Environment, pos: int):
        self.env = env
        self.pos = pos
        super().__init__(text)
        self.clicked.connect(self.clickCallback)

    def clickCallback(self):
        account = self.env.accountList[self.pos]
        if not self.env.offlineMode:
            try:
                self.env.account = getAccountDict(minecraft_launcher_lib.microsoft_account.complete_refresh(self.env.secrets.client_id, self.env.secrets.secret, self.env.secrets.redirect_url, account["refreshToken"]))
                self.env.mainWindow.updateAccountInformation()
                self.env.selectedAccount = self.pos
            except minecraft_launcher_lib.exceptions.InvalidRefreshToken:
                self.env.loginWindow.reset()
                self.env.loginWindow.show()
        else:
            self.env.account = self.env.accountList[self.pos]
            self.env.mainWindow.updateAccountInformation()
            self.env.selectedAccount = self.pos


class AccountTab(QTableWidget):
    def __init__(self, env: Environment):
        super().__init__(0, 2)
        self.env = env

        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setHorizontalHeaderLabels((QCoreApplication.translate("MainWindow", "Name"), QCoreApplication.translate("MainWindow", "Switch")))
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.verticalHeader().hide()
        self.updateAccountList()

    def updateAccountList(self):
        self.setRowCount(0)
        count = 0
        for i in self.env.accountList:
            nameItem = QTableWidgetItem(i["name"])
            nameItem.setFlags(nameItem.flags() ^ Qt.ItemFlag.ItemIsEditable)
            button = SwitchAccountButton(QCoreApplication.translate("MainWindow", "Switch"), self.env,count)
            self.insertRow(count)
            self.setItem(count, 0, nameItem)
            self.setCellWidget(count, 1, button)
            count += 1

    def addAccount(self):
        self.env.loginWindow.reset()
        self.env.loginWindow.show()

    def contextMenuEvent(self, event):
        menu = QMenu(self)

        addAccountAction = QAction(QCoreApplication.translate("MainWindow", "New Account"), self)
        addAccountAction.triggered.connect(self.addAccount)
        menu.addAction(addAccountAction)

        menu.popup(QCursor.pos())

class AboutTab(QWidget):
    def __init__(self, env: Environment):
        super().__init__()

        self.titleLabel = QLabel("jdMinecraftLauncher " + env.launcherVersion)
        self.fanmadeLabel = QLabel(QCoreApplication.translate("MainWindow", "This Launcher is fanmade and not from Mojang/Microsoft"))
        self.dependencyLabel = QLabel(QCoreApplication.translate("MainWindow", "This Program uses minecraft-launcher-lib {{version}}").replace("{{version}}", minecraft_launcher_lib.utils.get_library_version()))
        self.licenseLabel = QLabel(QCoreApplication.translate("MainWindow", "This Program is licensed under GPL 3.0"))
        self.viewSourceButton = QPushButton(QCoreApplication.translate("MainWindow", "View Source"))
        copyrightLabel = QLabel("Copyright © 2019-2023 JakobDev")

        self.viewSourceButton.clicked.connect(lambda: webbrowser.open("https://codeberg.org/JakobDev/jdMinecraftLauncher"))

        self.titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.fanmadeLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dependencyLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.licenseLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        copyrightLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.mainLayout = QGridLayout()
        self.mainLayout.addWidget(QLabel(),0,0)
        self.mainLayout.addWidget(QLabel(),0,2)
        self.mainLayout.addWidget(self.titleLabel,0,1)
        self.mainLayout.addWidget(self.fanmadeLabel,1,1)
        self.mainLayout.addWidget(self.dependencyLabel,2,1)
        self.mainLayout.addWidget(self.licenseLabel,3,1)
        self.mainLayout.addWidget(copyrightLabel, 4, 1)
        self.mainLayout.addWidget(self.viewSourceButton, 5, 1)
        self.setLayout(self.mainLayout)


class GameOutputTab(QPlainTextEdit):
    def __init__(self, env: Environment) -> None:
        super().__init__()
        self.env = env
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setReadOnly(True)

    def dataReady(self) -> None:
        cursor = self.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(bytes(self.process.readAll()).decode(encoding=sys.stdout.encoding,errors="replace"))
        self.moveCursor(cursor.MoveOperation.End)

    def procStarted(self) -> None:
        if self.profile.launcherVisibility != 2:
            self.env.mainWindow.hide()
        self.env.mainWindow.playButton.setEnabled(self.env.settings.get("enableMultiLaunch"))

    def procFinish(self) -> None:
        if self.profile.launcherVisibility == 0:
            self.env.mainWindow.show()
            self.env.mainWindow.setFocus()
        elif self.profile.launcherVisibility == 1:
            self.env.mainWindow.close()
        self.env.mainWindow.playButton.setEnabled(True)
        if self.natives_path != "":
            try:
                shutil.rmtree(self.natives_path)
            except Exception:
                pass

    def executeCommand(self,profile: Profile, command: List[str], natives_path: str) -> None:
        self.profile = profile
        self.natives_path = natives_path
        self.process = QProcess(self)
        self.process.setWorkingDirectory(self.env.minecraftDir)
        self.process.readyRead.connect(self.dataReady)
        self.process.started.connect(self.procStarted)
        self.process.finished.connect(self.procFinish)
        self.process.start(command[0], command[1:])

        if not self.process.waitForStarted():
            self.setPlainText(QCoreApplication.translate("MainWindow", "Failed to start Minecraft"))
            QMessageBox.critical(self, QCoreApplication.translate("MainWindow", "Failed to start"), QCoreApplication.translate("MainWindow", "Minecraft could not be started. Maybe you use a invalid Java executable."))
            self.env.mainWindow.playButton.setEnabled(True)
            return


class Tabs(QTabWidget):
    def __init__(self, env: Environment, parent: "MainWindow"):
        super().__init__()
        QWebEngineProfile.defaultProfile().setHttpAcceptLanguage(QLocale.system().name())
        QWebEngineProfile.defaultProfile().setHttpUserAgent("jdMinecraftLauncher/" + env.launcherVersion)
        webView = QWebEngineView()
        webView.load(QUrl(env.settings.get("newsURL")))
        self.addTab(webView, QCoreApplication.translate("MainWindow", "News"))
        self.profileEditor = ProfileEditorTab(env, parent)
        self.addTab(self.profileEditor, QCoreApplication.translate("MainWindow", "Profile Editor"))
        self.versionTab = VersionEditorTab(env)
        self.addTab(self.versionTab, QCoreApplication.translate("MainWindow", "Version Editor"))
        self.options = OptionsTab(env, parent)
        self.addTab(self.options, QCoreApplication.translate("MainWindow", "Options"))
        if not env.offlineMode:
            self.forgeTab = ForgeTab(env, parent)
            self.addTab(self.forgeTab, "Forge")
            self.fabricTab = FabricTab(env, parent)
            self.addTab(self.fabricTab, "Fabric")
        self.accountTab = AccountTab(env)
        self.addTab(self.accountTab, QCoreApplication.translate("MainWindow", "Account"))
        about = AboutTab(env)
        self.addTab(about, QCoreApplication.translate("MainWindow", "About"))

    def updateProfiles(self):
        self.profileEditor.updateProfiles()

class MainWindow(QWidget):
    def __init__(self, env: Environment):
        super().__init__()
        self.env = env
        self.profileListRebuild = False
        self.windowIconProgress = createWindowIconProgress(self)
        self.tabWidget = Tabs(env, self)
        self.profileWindow = ProfileWindow(self.env,self)
        self.progressBar = QProgressBar()
        self.profileComboBox = QComboBox()
        self.profilLabel = QLabel(QCoreApplication.translate("MainWindow", "Profile:"))
        self.newProfileButton = QPushButton(QCoreApplication.translate("MainWindow", "New Profile"))
        self.editProfileButton = QPushButton(QCoreApplication.translate("MainWindow", "Edit Profile"))
        self.playButton = QPushButton(QCoreApplication.translate("MainWindow", "Play"))
        self.accountLabel = QLabel()
        self.accountButton = QPushButton(QCoreApplication.translate("MainWindow", "Logout"))

        self.progressBar.setTextVisible(True)
        self.profileComboBox.setCurrentIndex(self.env.selectedProfile)
        self.playButton.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Preferred,QSizePolicy.Policy.Minimum))

        self.newProfileButton.clicked.connect(self.newProfileButtonClicked)
        self.editProfileButton.clicked.connect(self.editProfileButtonClicked)
        self.playButton.clicked.connect(self.playButtonClicked)
        self.accountButton.clicked.connect(self.logoutButtonClicked)
        self.profileComboBox.currentIndexChanged.connect(self.profileComboBoxIndexChanged)

        self.profileSelectLayout = QHBoxLayout()
        self.profileSelectLayout.addWidget(self.profilLabel)
        self.profileSelectLayout.addWidget(self.profileComboBox)

        self.profileButtonsLayout = QHBoxLayout()
        self.profileButtonsLayout.addWidget(self.newProfileButton)
        self.profileButtonsLayout.addWidget(self.editProfileButton)

        self.profileLayout = QVBoxLayout()
        self.profileLayout.addLayout(self.profileSelectLayout)
        self.profileLayout.addLayout(self.profileButtonsLayout)

        self.accountLayout = QVBoxLayout()
        self.accountLayout.addWidget(self.accountLabel)
        self.accountLayout.addWidget(self.accountButton)

        self.barLayout = QHBoxLayout()
        self.barLayout.addLayout(self.profileLayout)
        self.barLayout.addWidget(self.playButton)
        self.barLayout.addLayout(self.accountLayout)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.tabWidget)
        self.mainLayout.addWidget(self.progressBar)
        self.mainLayout.addLayout(self.barLayout)

        self.updateProfileList()
    
        self.setWindowTitle("jdMinecraftLauncher")
        self.setLayout(self.mainLayout)

        self.installThread = InstallThread(env)
        self.installThread.text.connect(lambda text: self.progressBar.setFormat(text))
        self.installThread.progress.connect(self.updateProgress)
        self.installThread.progress_max.connect(lambda progress_max: self.progressBar.setMaximum(progress_max))
        self.installThread.finished.connect(self.installFinish)

        self._is_first_open = False

    def openMainWindow(self):
        if self._is_first_open:
            self.show()
            return

        if platform.system() == "Linux":
            from jdMinecraftLauncher.DBusService import DBusService
            DBusService(self.env, self.env.app)

        if self.env.args.launch_profile:
            profile = self.env.profileCollection.getProfileByName(self.env.args.launch_profile)
            if profile:
                self.env.mainWindow.launchProfile(profile)
            else:
                QMessageBox.critical(self, QCoreApplication.translate("MainWindow", "Profile not found"), QCoreApplication.translate("MainWindow", "The given Profile was not found"))
        elif self.env.args.url:
            parse_results = urllib.parse.urlparse(self.env.args.url)
            if parse_results.scheme == "jdminecraftlauncher":
                self._handleCustomURL(parse_results.path)

        self._is_first_open = True
        self.show()

    def _handleCustomURL(self, args: str) -> None:
        try:
            method, param = args.split("/", 1)
        except ValueError:
            return

        if method == "LaunchProfileByID":
            profile = self.env.profileCollection.getProfileByID(param)
            if profile:
                self.env.profileCollection.mainWindow.launchProfile(profile)
            else:
                QMessageBox.critical(self, QCoreApplication.translate("MainWindow", "Profile not found"), QCoreApplication.translate("MainWindow", "The given Profile was not found"))
        elif method == "LaunchProfileByName":
            profile = self.profileCollection.env.getProfileByName(param)
            if profile:
                self.env.mainWindow.launchProfile(profile)
            else:
                QMessageBox.critical(self, QCoreApplication.translate("MainWindow", "Profile not found"), QCoreApplication.translate("MainWindow", "The given Profile was not found"))

    def updateProfileList(self):
        currentIndex = 0
        self.profileListRebuild = True
        self.profileComboBox.clear()
        for count, i in enumerate(self.env.profileCollection.profileList):
            self.profileComboBox.addItem(i.name)
            if i.id == self.env.profileCollection.selectedProfile:
                currentIndex = count
        self.tabWidget.updateProfiles()
        self.profileComboBox.setCurrentIndex(currentIndex)
        self.profileListRebuild = False

    def profileComboBoxIndexChanged(self, index: int):
        if not self.profileListRebuild:
            self.env.profileCollection.selectedProfile = self.env.profileCollection.profileList[index].id
        
    def newProfileButtonClicked(self):
        self.profileWindow.loadProfile(self.env.profileCollection.getSelectedProfile(), True, True)
        self.profileWindow.exec()

    def editProfileButtonClicked(self):
        self.profileWindow.loadProfile(self.env.profileCollection.getSelectedProfile(), False)
        self.profileWindow.exec()

    def launchProfile(self, profile: Profile) -> None:
        if self.env.offlineMode:
            if os.path.isdir(os.path.join(self.env.minecraftDir,"versions",profile.getVersionID())):
                self.startMinecraft(profile)
            else:
                QMessageBox.critical(self, QCoreApplication.translate("MainWindow", "No Internet Connection"), QCoreApplication.translate("MainWindow", "You need a internet connection to install a new version, but you are still able to play already installed versions."))
        else:
            self.installVersion(profile)

    def playButtonClicked(self):
        self.launchProfile(self.env.profileCollection.getSelectedProfile())

    def logoutButtonClicked(self):
        if self.env.offlineMode:
            QMessageBox.critical(self, QCoreApplication.translate("MainWindow", "No Internet Connection"), QCoreApplication.translate("MainWindow", "This Feature needs a internet connection"))
            return
        del self.env.accountList[self.env.selectedAccount]
        if len(self.env.accountList) == 0:
            self.hide()
            self.env.loginWindow.show()
            self.env.loginWindow.setFocus()
        else:
            self.env.account = self.env.accountList[0]
            self.updateAccountInformation()

    def startMinecraft(self, profile: Profile):
        if self.env.settings.get("extractNatives"):
            natives_path = os.path.join(tempfile.gettempdir(), "minecraft_natives_" + str(random.randrange(0, 10000000)))
        else:
            natives_path = ""
        args = getMinecraftCommand(self.env.profileCollection.getSelectedProfile(), self.env, natives_path)
        o = GameOutputTab(self.env)
        tabid = self.tabWidget.addTab(o, QCoreApplication.translate("MainWindow", "Game Output"))
        self.tabWidget.setCurrentIndex(tabid)
        o.executeCommand(profile,args,natives_path)

    def installFinish(self) -> None:
        self.windowIconProgress.hide()

        if self.installThread.getError() is not None:
            text = QCoreApplication.translate("MainWindow", "Due to an error, the installation could not be completed") + "<br><br>"
            text += QCoreApplication.translate("MainWindow", "This may have been caused by a network error")

            msgBox = QMessageBox()
            msgBox.setWindowTitle(QCoreApplication.translate("MainWindow", "Installation failed"))
            msgBox.setText(text)
            msgBox.setDetailedText(self.installThread.getError())
            msgBox.exec()

            self.progressBar.setValue(0)
            self.progressBar.setFormat("")
            self.setInstallButtonsEnabled(True)

            return

        if self.installThread.shouldStartMinecraft() and self.installThread.getError() is None:
            self.env.updateInstalledVersions()
            self.tabWidget.versionTab.updateVersions()
            self.startMinecraft(self.env.current_running_profile)
        else:
            self.env.loadVersions()
            self.profileWindow.updateVersionsList()
            self.setInstallButtonsEnabled(True)

    def installVersion(self, profile: Profile):
        self.env.current_running_profile = profile
        self.playButton.setEnabled(False)
        self.installThread.setup(profile)
        self.installThread.start()

    def updateAccountInformation(self):
        self.accountLabel.setText(QCoreApplication.translate("MainWindow", "Welcome, {{name}}").replace("{{name}}", self.env.account["name"]))
        self.tabWidget.accountTab.updateAccountList()
        if self.env.offlineMode:
            self.playButton.setText(QCoreApplication.translate("MainWindow", "Play Offline"))
        else:
            self.playButton.setText(QCoreApplication.translate("MainWindow", "Play"))

    def setInstallButtonsEnabled(self, enabled: bool):
        self.playButton.setEnabled(enabled)
        self.tabWidget.forgeTab.setButtonsEnabled(enabled)
        self.tabWidget.fabricTab.setButtonsEnabled(enabled)

    def updateProgress(self, progress: int) -> None:
        self.progressBar.setValue(progress)

        if self.env.settings.get("windowIconProgress"):
            self.windowIconProgress.setProgress(progress / self.progressBar.maximum())

    def event(self, event: QEvent) -> bool:
        if event.type() == QEvent.Type.WinIdChange:
            self.windowIconProgress = createWindowIconProgress(self)

        return super().event(event)

    def closeEvent(self,event):
        if self.env.args.dont_save_data:
            event.accept()
            sys.exit(0)

        options = self.tabWidget.options
        self.env.profileCollection.save()
        self.env.settings.set("language", options.languageComboBox.currentData())
        self.env.settings.set("newsURL", options.urlEdit.text())
        self.env.settings.set("enableMultiLaunch", options.allowMultiLaunchCheckBox.isChecked())
        self.env.settings.set("extractNatives", options.extractNativesCheckBox.isChecked())
        self.env.settings.save(os.path.join(self.env.dataDir, "settings.json"))
        with open(os.path.join(self.env.dataDir, "microsoft_accounts.json"),"w") as f:
            data = {}
            data["selectedAccount"] = self.env.selectedAccount
            data["accountList"] = []
            for count, i in enumerate(self.env.accountList):
                if i["name"] in self.env.disableAccountSave:
                    if count == data["selectedAccount"]:
                        data["selectedAccount"] = 0
                else:
                    data["accountList"].append(i)
            json.dump(data, f, ensure_ascii=False, indent=4)
        event.accept()
        sys.exit(0)
