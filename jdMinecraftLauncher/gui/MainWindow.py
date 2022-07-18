from PyQt6.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout, QGridLayout, QPlainTextEdit, QTabWidget, QAbstractItemView, QHeaderView, QPushButton, QComboBox, QProgressBar, QLabel, QCheckBox, QMenu, QLineEdit, QSizePolicy, QMessageBox
from PyQt6.QtCore import QUrl, QLocale, Qt, QProcess
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile
from PyQt6.QtGui import QCursor, QAction, QIcon
from jdMinecraftLauncher.gui.ProfileWindow import ProfileWindow
from jdMinecraftLauncher.Profile import Profile
from jdMinecraftLauncher.Functions import openFile, saveProfiles, showMessageBox, createDesktopFile
from jdMinecraftLauncher.InstallThread import InstallThread
from jdMinecraftLauncher.RunMinecraft import getMinecraftCommand
import minecraft_launcher_lib
import webbrowser
import subprocess
import platform
import tempfile
import random
import shutil
import json
import sys
import os

class ProfileEditorTab(QTableWidget):
    def __init__(self,env,mainwindow):
        super().__init__(0,2)
        self.env = env
        self.mainWindow = mainwindow
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setHorizontalHeaderLabels((self.env.translate("profiletab.profileName"),self.env.translate("profiletab.minecraftVersion")))
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.verticalHeader().hide()
        self.setShowGrid(False)
        self.updateProfiles()

    def updateProfiles(self):
        while (self.rowCount() > 0):
            self.removeRow(0)
        count = 0
        for i in self.env.profiles:
            nameItem = QTableWidgetItem(i.name)
            nameItem.setFlags(nameItem.flags() ^ Qt.ItemFlag.ItemIsEditable)
            if i.useLatestVersion:
                versionItem = QTableWidgetItem(self.env.translate("profiletab.latestVersion"))
            else:
                versionItem = QTableWidgetItem(i.version)
            versionItem.setFlags(versionItem.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.insertRow(count)
            self.setItem(count, 0, nameItem) 
            self.setItem(count, 1, versionItem) 
            count += 1

    def contextMenuEvent(self, event):
        self.menu = QMenu(self)

        addProfile = QAction(self.env.translate("profiletab.contextmenu.addProfile"), self)
        addProfile.triggered.connect(self.addProfile)
        self.menu.addAction(addProfile)
    
        editProfile = QAction(self.env.translate("profiletab.contextmenu.editProfile"), self)
        editProfile.triggered.connect(self.editProfile)
        self.menu.addAction(editProfile)

        copyProfile = QAction(self.env.translate("profiletab.contextmenu.copyProfile"), self)
        copyProfile.triggered.connect(self.copyProfile)
        self.menu.addAction(copyProfile)

        removeProfile = QAction(self.env.translate("profiletab.contextmenu.removeProfile"), self)
        removeProfile.triggered.connect(self.removeProfile)
        self.menu.addAction(removeProfile)

        openGameFolder = QAction(self.env.translate("profiletab.contextmenu.openGameFolder"), self)
        openGameFolder.triggered.connect(lambda: openFile(self.env.profiles[self.currentRow()].getGameDirectoryPath()))
        self.menu.addAction(openGameFolder)

        if platform.system() == "Linux":
            createShortcut = QAction(self.env.translate("profiletab.contextmenu.createShortcut"), self)
            createShortcut.triggered.connect(self.createShortcut)
            self.menu.addAction(createShortcut)

        self.menu.popup(QCursor.pos())

    def addProfile(self):
        self.mainWindow.profileWindow.loadProfile(Profile(self.env.translate("profiletab.newProfile"),self.env),True)
        self.mainWindow.profileWindow.show()
        self.mainWindow.profileWindow.setFocus()

    def editProfile(self):
        self.mainWindow.profileWindow.loadProfile(self.env.profiles[self.currentRow()],False)
        self.mainWindow.profileWindow.show()
        self.mainWindow.profileWindow.setFocus()

    def copyProfile(self):
        self.mainWindow.profileWindow.loadProfile(self.env.profiles[self.currentRow()],True,True)
        self.mainWindow.profileWindow.show()
        self.mainWindow.profileWindow.setFocus()

    def removeProfile(self):
        if len(self.env.profiles) == 1:
            showMessageBox("profiletab.removeError.title","profiletab.removeError.text",self.env)
        else:
            del self.env.profiles[self.currentRow()]
            self.env.selectedProfile = 0
            self.mainWindow.updateProfilList()

    def createShortcut(self):
        box = QMessageBox()
        box.setText(self.env.translate("profiletab.createShortcut.text"))
        box.setWindowTitle(self.env.translate("profiletab.createShortcut.title"))
        box.setStandardButtons(QMessageBox.StandardButton.Save| QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)

        desktopButton = box.button(QMessageBox.StandardButton.Save)
        desktopButton.setText(self.env.translate("profiletab.createShortcut.desktop"))
        desktopButton.setIcon(QIcon())

        menuButton = box.button(QMessageBox.StandardButton.Discard )
        menuButton.setText(self.env.translate("profiletab.createShortcut.menu"))
        menuButton.setIcon(QIcon())

        bothButton = box.button(QMessageBox.StandardButton.Cancel)
        bothButton.setText(self.env.translate("profiletab.createShortcut.both"))
        bothButton.setIcon(QIcon())

        name = self.env.profiles[self.currentRow()].name
        box.exec()

        if box.clickedButton() == desktopButton:
            createDesktopFile(subprocess.check_output(["xdg-user-dir", "DESKTOP"]).decode("utf-8").strip(), name)
        elif box.clickedButton() == menuButton:
            createDesktopFile(os.path.expanduser("~/.local/share/applications"), name)
        elif box.clickedButton() == bothButton:
            createDesktopFile(subprocess.check_output(["xdg-user-dir", "DESKTOP"]).decode("utf-8").strip(), name)
            createDesktopFile(os.path.expanduser("~/.local/share/applications"), name)

class VersionEditorTab(QTableWidget):
    def __init__(self,env):
        super().__init__(0,2)
        self.env = env

        self.uninstallVersion = QAction(self.env.translate("versiontab.contextmenu.uninstallVersion"), self)
        self.uninstallVersion.triggered.connect(self.uninstallVersionClicked)

        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setHorizontalHeaderLabels((self.env.translate("versiontab.minecraftVersion"),self.env.translate("versiontab.versionType")))
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
        while (self.rowCount() > 0):
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

    def contextMenuEvent(self, event):
        self.menu = QMenu(self)

        self.menu.addAction(self.uninstallVersion)

        self.menu.popup(QCursor.pos())

    def uninstallVersionClicked(self):
        shutil.rmtree(os.path.join(self.env.minecraftDir,"versions",self.env.installedVersion[self.currentRow()]["id"]))
        del self.env.installedVersion[self.currentRow()]
        self.updateVersions()

class OptionsTab(QWidget):
    def __init__(self,env):
        self.env = env
        super().__init__()
        self.languageComboBox = QComboBox()
        self.urlEdit = QLineEdit()
        self.allowMultiLaunchCheckBox = QCheckBox(env.translate("optionstab.checkBox.allowMultiLaunch"))
        self.extractNativesCheckBox = QCheckBox(env.translate("optionstab.checkBox.extractNatives"))

        self.languageComboBox.addItem(env.translate("optionstab.combobox.systemLanguage"),"default")
        for i in os.listdir(os.path.join(env.currentDir,"translation")):
            self.languageComboBox.addItem(env.translate("language." + i[:-5],default=i[:-5]),i[:-5])

        for i in range(self.languageComboBox.count()):
            if self.languageComboBox.itemData(i) == env.settings.language:
                self.languageComboBox.setCurrentIndex(i)

        self.urlEdit.setText(env.settings.newsURL)
        self.allowMultiLaunchCheckBox.setChecked(self.env.settings.enableMultiLaunch)
        self.extractNativesCheckBox.setChecked(self.env.settings.extractNatives)

        self.allowMultiLaunchCheckBox.stateChanged.connect(self.multiLaunchCheckBoxChanged)
        self.extractNativesCheckBox.stateChanged.connect(self.extractNativesCheckBoxChanged)

        gridLayout = QGridLayout()
        gridLayout.addWidget(QLabel(env.translate("optionstab.label.language")),0,0)
        gridLayout.addWidget(self.languageComboBox,0,1)
        gridLayout.addWidget(QLabel(env.translate("optionstab.label.newsURL")),1,0)
        gridLayout.addWidget(self.urlEdit,1,1)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(gridLayout)
        mainLayout.addWidget(self.allowMultiLaunchCheckBox)
        mainLayout.addWidget(self.extractNativesCheckBox)
        mainLayout.addStretch(1)
        
        self.setLayout(mainLayout)

    def multiLaunchCheckBoxChanged(self):
        self.env.settings.enableMultiLaunch = bool(self.allowMultiLaunchCheckBox.checkState())

    def extractNativesCheckBoxChanged(self):
        self.env.settings.extractNatives = bool(self.extractNativesCheckBox.checkState())

class SwitchAccountButton(QPushButton):
    def __init__(self,text,env,pos):
        self.env = env
        self.pos = pos
        super().__init__(text)
        self.clicked.connect(self.clickCallback)

    def clickCallback(self):
        account = self.env.accountList[self.pos]
        if minecraft_launcher_lib.account.validate_access_token(account["accessToken"]):
            self.env.account = self.env.accountList[self.pos]
            self.env.mainWindow.updateAccountInformation()
            self.env.selectedAccount = self.pos
        else:
            # self.env.loginWindow.reset()
            # self.env.loginWindow.setName(account.get("mail",""))
            self.env.loginWindow.show()

class ForgeTab(QTableWidget):
    def __init__(self, env, mainWindow):
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
        for i in minecraft_launcher_lib.forge.list_forge_versions():
            minecraft_version, _ = i.split("-", 1)

            if minecraft_version in minecraft_version_check or not minecraft_launcher_lib.forge.supports_automatic_install(i):
                continue

            minecraft_version_check[minecraft_version] = True

            versionItem = QTableWidgetItem(i)
            versionItem.setFlags(versionItem.flags() ^ Qt.ItemFlag.ItemIsEditable)

            installButton = QPushButton(env.translate("mainwindow.button.install"))

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
    def __init__(self, env, mainWindow):
        self.env = env
        self.mainWindow = mainWindow
        super().__init__(0,2)

        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.horizontalHeader().hide()
        self.verticalHeader().hide()

        count = 0
        for i in minecraft_launcher_lib.fabric.get_all_minecraft_versions():
            if not i["stable"]:
                continue

            versionItem = QTableWidgetItem(i["version"])
            versionItem.setFlags(versionItem.flags() ^ Qt.ItemFlag.ItemIsEditable)

            installButton = QPushButton(env.translate("mainwindow.button.install"))

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


class AccountTab(QTableWidget):
    def __init__(self,env):
        self.env = env
        super().__init__(0,2)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setHorizontalHeaderLabels((self.env.translate("accounttab.nameHeader"),self.env.translate("accounttab.switchHeader")))
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
            button = SwitchAccountButton(self.env.translate("accounttab.button.switch"),self.env,count)
            self.insertRow(count)
            self.setItem(count, 0, nameItem)
            self.setCellWidget(count,1,button)
            # self.setItem(count, 1, versionItem) 
            count += 1

    def addAccount(self):
        self.env.loginWindow.show()

    def contextMenuEvent(self, event):
        menu = QMenu(self)

        addAccountAction = QAction(self.env.translate("account.newAccount"), self)
        addAccountAction.triggered.connect(self.addAccount)
        menu.addAction(addAccountAction)

        menu.popup(QCursor.pos())

class AboutTab(QWidget):
    def __init__(self,env):
        super().__init__()
        self.titleLabel = QLabel(env.translate("abouttab.label.title") % env.launcherVersion)
        self.fanmadeLabel = QLabel(env.translate("abouttab.label.fanmade"))
        self.dependencyLabel = QLabel(env.translate("abouttab.label.dependency").format(version=minecraft_launcher_lib.utils.get_library_version()))
        self.licenseLabel = QLabel(env.translate("abouttab.label.license"))
        self.viewSourceButton = QPushButton(env.translate("abouttab.button.viewSource"))

        self.viewSourceButton.clicked.connect(lambda: webbrowser.open("https://gitlab.com/JakobDev/jdMinecraftLauncher"))

        self.titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.fanmadeLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dependencyLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.licenseLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.mainLayout = QGridLayout()
        self.mainLayout.addWidget(QLabel(),0,0)
        self.mainLayout.addWidget(QLabel(),0,2)
        self.mainLayout.addWidget(self.titleLabel,0,1)
        self.mainLayout.addWidget(self.fanmadeLabel,1,1)
        self.mainLayout.addWidget(self.dependencyLabel,2,1)
        self.mainLayout.addWidget(self.licenseLabel,3,1)
        self.mainLayout.addWidget(self.viewSourceButton,4,1)
        self.setLayout(self.mainLayout)

class GameOutputTab(QPlainTextEdit):
    def __init__(self,env):
        super().__init__()
        self.env = env
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setReadOnly(True)

    def dataReady(self):
        cursor = self.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(bytes(self.process.readAll()).decode(encoding=sys.stdout.encoding,errors="replace"))
        self.moveCursor(cursor.MoveOperation.End)

    def procStarted(self):
        if self.env.settings.enableMultiLaunch:
            self.env.mainWindow.playButton.setEnabled(True)
            return
        if self.profile.launcherVisibility != 2:
            self.env.mainWindow.hide()
        self.env.mainWindow.playButton.setEnabled(False)

    def procFinish(self):
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

    def executeCommand(self,profile, command, natives_path):
        self.profile = profile
        self.natives_path = natives_path
        self.process = QProcess(self)
        self.process.setWorkingDirectory(self.env.minecraftDir)
        self.process.readyRead.connect(self.dataReady)
        self.process.started.connect(self.procStarted)
        self.process.finished.connect(self.procFinish)
        self.process.start(command[0], command[1:])

class Tabs(QTabWidget):
    def __init__(self,env,parrent):
        super().__init__()
        QWebEngineProfile.defaultProfile().setHttpAcceptLanguage(QLocale.system().name())
        QWebEngineProfile.defaultProfile().setHttpUserAgent("jdMinecraftLauncher/" + env.launcherVersion)
        webView = QWebEngineView()
        webView.load(QUrl(env.settings.newsURL))
        self.addTab(webView,env.translate("mainwindow.tab.news"))
        self.profileEditor = ProfileEditorTab(env,parrent)
        self.addTab(self.profileEditor,env.translate("mainwindow.tab.profileEditor"))
        self.versionTab = VersionEditorTab(env)
        self.addTab(self.versionTab,env.translate("mainwindow.tab.versionEditor"))
        self.options = OptionsTab(env)
        self.addTab(self.options,env.translate("mainwindow.tab.options"))
        if not env.offlineMode:
            self.forgeTab = ForgeTab(env, parrent)
            self.addTab(self.forgeTab, "Forge")
            self.fabricTab = FabricTab(env, parrent)
            self.addTab(self.fabricTab, "Fabric")
        self.accountTab = AccountTab(env)
        self.addTab(self.accountTab,"Account")
        about = AboutTab(env)
        self.addTab(about,env.translate("mainwindow.tab.about"))

    def updateProfiles(self):
        self.profileEditor.updateProfiles()

class MainWindow(QWidget):
    def __init__(self, enviroment):
        super().__init__()
        self.env = enviroment
        self.tabWidget = Tabs(enviroment,self)
        self.profileWindow = ProfileWindow(self.env,self)
        self.progressBar = QProgressBar()
        self.profileComboBox = QComboBox()
        self.profilLabel = QLabel(self.env.translate("mainwindow.label.profile"))
        self.newProfileButton = QPushButton(self.env.translate("mainwindow.button.newProfile"))
        self.editProfileButton = QPushButton(self.env.translate("mainwindow.button.editProfile"))
        self.playButton = QPushButton(self.env.translate("mainwindow.button.play"))
        self.accountLabel = QLabel()
        self.accountButton = QPushButton(self.env.translate("mainwindow.button.logout"))

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
        #self.profileLayout.addWidget(self.profilLabel,0,0)
        #self.profileLayout.addWidget(self.profileComboBox,0,1)
        #self.profileLayout.addWidget(self.newProfileButton,1,0)
        #self.profileLayout.addWidget(self.editProfileButton,1,1)

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

        self.updateProfilList()
    
        self.setWindowTitle("jdMinecraftLauncher")
        self.setLayout(self.mainLayout)

        self.installThread = InstallThread(enviroment)
        self.installThread.text.connect(lambda text: self.progressBar.setFormat(text))
        self.installThread.progress.connect(lambda progress: self.progressBar.setValue(progress))
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
            profile = self.env.getProfileByName(self.env.args.launch_profile)
            if profile:
                self.env.mainWindow.launchProfile(profile)

        self._is_first_open = True
        self.show()

    def updateProfilList(self):
        currentIndex = self.env.selectedProfile
        self.profileComboBox.clear()
        for i in self.env.profiles:
            self.profileComboBox.addItem(i.name)
        self.tabWidget.updateProfiles()
        self.profileComboBox.setCurrentIndex(currentIndex)

    def profileComboBoxIndexChanged(self, index):
        self.env.selectedProfile = index
        
    def newProfileButtonClicked(self):
        self.profileWindow.loadProfile(self.env.profiles[self.profileComboBox.currentIndex()],True,True)
        self.profileWindow.show()
        self.profileWindow.setFocus()

    def editProfileButtonClicked(self):
        self.profileWindow.loadProfile(self.env.profiles[self.profileComboBox.currentIndex()],False)
        self.profileWindow.show()
        self.profileWindow.setFocus()

    def launchProfile(self, profile: Profile) -> None:
        if self.env.offlineMode:
            if os.path.isdir(os.path.join(self.env.minecraftDir,"versions",profile.getVersionID())):
                self.startMinecraft(profile)
            else:
                showMessageBox("messagebox.installinternet.title","messagebox.installinternet.text",self.env)
        else:
            self.installVersion(profile)

    def playButtonClicked(self):
        profile = self.env.profiles[self.profileComboBox.currentIndex()]
        self.launchProfile(profile)

    def logoutButtonClicked(self):
        if self.env.offlineMode:
            showMessageBox("messagebox.needinternet.title","messagebox.needinternet.text",self.env)
            return
        del self.env.accountList[self.env.selectedAccount]
        if len(self.env.accountList) == 0:
            self.hide()
            self.env.loginWindow.show()
            self.env.loginWindow.setFocus()
        else:
            self.env.account = self.env.accountList[0]
            self.updateAccountInformation()

    def startMinecraft(self,profile):
        if self.env.settings.extractNatives:
            natives_path = os.path.join(tempfile.gettempdir(),"minecraft_natives_" + str(random.randrange(0,10000000)))
        else:
            natives_path = ""
        args = getMinecraftCommand(self.env.profiles[self.profileComboBox.currentIndex()], self.env, natives_path)
        o = GameOutputTab(self.env)
        tabid = self.tabWidget.addTab(o,self.env.translate("mainwindow.tab.gameOutput"))
        self.tabWidget.setCurrentIndex(tabid)
        o.executeCommand(profile,args,natives_path)

    def installFinish(self):
        if self.installThread.shouldStartMinecraft():
            self.env.updateInstalledVersions()
            self.tabWidget.versionTab.updateVersions()
            self.startMinecraft(self.env.current_running_profile)
        else:
            self.env.loadVersions()
            self.profileWindow.updateVersionsList
            self.setInstallButtonsEnabled(True)

    def installVersion(self,profile):
        self.env.current_running_profile = profile
        self.playButton.setEnabled(False)
        self.installThread.setup(profile)
        self.installThread.start()

    def updateAccountInformation(self):
        self.accountLabel.setText(self.env.translate("mainwindow.label.account") % self.env.account["name"])
        self.tabWidget.accountTab.updateAccountList()
        if self.env.offlineMode:
            self.playButton.setText(self.env.translate("mainwindow.button.playOffline"))
        else:
            self.env.translate("mainwindow.button.play")

    def setInstallButtonsEnabled(self, enabled: bool):
        self.playButton.setEnabled(enabled)
        self.tabWidget.forgeTab.setButtonsEnabled(enabled)
        self.tabWidget.fabricTab.setButtonsEnabled(enabled)

    def closeEvent(self,event):
        options = self.tabWidget.options
        self.env.settings.language = options.languageComboBox.currentData()
        self.env.settings.newsURL = options.urlEdit.text()
        self.env.settings.enableMultiLaunch = options.allowMultiLaunchCheckBox.isChecked()
        self.env.settings.extractNatives = options.extractNativesCheckBox.isChecked()
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
        saveProfiles(self.env)
        event.accept()
        sys.exit(0)
