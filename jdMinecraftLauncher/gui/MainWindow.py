from PyQt5.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout, QGridLayout, QPlainTextEdit, QTabWidget, QAbstractItemView, QHeaderView, QAction, QPushButton, QComboBox, QProgressBar, QLabel, QFileDialog, QMenu
from PyQt5.QtCore import QUrl, QLocale, Qt, QDir, QProcess
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtGui import QPixmap, QCursor
from jdMinecraftLauncher.gui.ProfileWindow import ProfileWindow
from jdMinecraftLauncher.Profile import Profile
from jdMinecraftLauncher.Functions import openFile, saveProfiles, showMessageBox
from jdMinecraftLauncher.InstallThread import InstallThread
from jdMinecraftLauncher.RunMinecraft import runMinecraft
import mojang_api
import webbrowser
import urllib
import shutil
import os

class ProfileEditorTab(QTableWidget):
    def __init__(self,env,mainwindow):
        super().__init__(0,2)
        self.env = env
        self.mainWindow = mainwindow
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setHorizontalHeaderLabels((self.env.translate("profiletab.profileName"),self.env.translate("profiletab.minecraftVersion")))
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.verticalHeader().hide()
        self.setShowGrid(False)
        self.updateProfiles()

    def updateProfiles(self):
        while (self.rowCount() > 0):
                self.removeRow(0)
        count = 0
        for i in self.env.profiles:
            nameItem = QTableWidgetItem(i.name)
            nameItem.setFlags(nameItem.flags() ^ Qt.ItemIsEditable)
            if i.useLatestVersion:
                versionItem = QTableWidgetItem(self.env.translate("profiletab.latestVersion"))
            else:
                versionItem = QTableWidgetItem(i.version)
            versionItem.setFlags(versionItem.flags() ^ Qt.ItemIsEditable)
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
            self.mainWindow.updateProfilList()
            saveProfiles(self.env)

class VersionEditorTab(QTableWidget):
    def __init__(self,env):
        super().__init__(0,2)
        self.env = env

        self.uninstallVersion = QAction(self.env.translate("versiontab.contextmenu.uninstallVersion"), self)
        self.uninstallVersion.triggered.connect(self.uninstallVersionClicked)

        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setHorizontalHeaderLabels((self.env.translate("versiontab.minecraftVersion"),self.env.translate("versiontab.versionType")))
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
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
            idItem.setFlags(idItem.flags() ^ Qt.ItemIsEditable)
            typeItem = QTableWidgetItem(i["type"])
            typeItem.setFlags(typeItem.flags() ^ Qt.ItemIsEditable)
            self.insertRow(count)
            self.setItem(count, 0, idItem) 
            self.setItem(count, 1, typeItem) 
            count += 1

    def contextMenuEvent(self, event):
        self.menu = QMenu(self)

        self.menu.addAction(self.uninstallVersion)

        self.menu.popup(QCursor.pos())

    def uninstallVersionClicked(self):
        shutil.rmtree(os.path.join(self.env.dataPath,"versions",self.env.installedVersion[self.currentRow()]["id"]))
        del self.env.installedVersion[self.currentRow()]
        self.updateVersions()

class SkinTab(QWidget):
    def __init__(self,env):
        super().__init__()
        self.env = env

        self.uploadButton = QPushButton(env.translate("skintab.button.uploadSkin"))
        self.resetButton = QPushButton(env.translate("skintab.button.resetSkin"))
        self.downloadButton = QPushButton(env.translate("skintab.button.downloadSkin"))

        self.picture = QLabel()
        self.picture.setPixmap(QPixmap(100,200))

        self.uploadButton.clicked.connect(self.uploadButtonClicked)
        self.resetButton.clicked.connect(self.resetButtonClicked)
        self.downloadButton.clicked.connect(self.downloadButtonClicked)

        self.skinLayout = QVBoxLayout()
        self.skinLayout.addWidget(QLabel(env.translate("skintab.label.currentSkin")))
        self.skinLayout.addWidget(self.picture)

        self.buttonLayout = QVBoxLayout()
        self.buttonLayout.addWidget(self.uploadButton)
        self.buttonLayout.addWidget(self.resetButton)
        self.buttonLayout.addWidget(self.downloadButton)

        self.mainLayout = QGridLayout()
        self.mainLayout.addLayout(self.skinLayout,0,0)
        self.mainLayout.addLayout(self.buttonLayout,0,1)
        
        self.setLayout(self.mainLayout)

    def updateSkin(self):
        path = os.path.join(self.env.dataPath,"Userskin_Front.png")
        if not self.env.offlineMode:
            if os.path.isfile(path):
                os.remove(path)
            urllib.request.urlretrieve('https://minotar.net/armor/body/%s/100.png' % self.env.account["uuid"],path)
        if os.path.isfile(path):
            self.picture.setPixmap(QPixmap(path))

    def uploadButtonClicked(self):
        if self.env.offlineMode:
            showMessageBox("messagebox.needinternet.title","messagebox.needinternet.text",self.env)
            return

        path = QFileDialog.getOpenFileName(self,self.env.translate("skintab.filepicker.upload.title"),self.env.translate("skintab.filepicker.filetype.png"))

        if path[0]:
            p = mojang_api.user.player.Player(self.env.account["name"],self.env.account["uuid"])
            mojang_api.servers.api.upload_skin(p,self.env.account["accessToken"],path[0])
            self.updateSkin()
            showMessageBox("skintab.upload.title","skintab.upload.text",self.env)

    def resetButtonClicked(self):
        if self.env.offlineMode:
            showMessageBox("messagebox.needinternet.title","messagebox.needinternet.text",self.env)
            return

        p = mojang_api.user.player.Player(self.env.account["name"],self.env.account["uuid"])
        mojang_api.servers.api.reset_skin(p,self.env.account["accessToken"])
        self.updateSkin()
        showMessageBox("skintab.reset.title","skintab.reset.text",self.env)

    def downloadButtonClicked(self):
        if self.env.offlineMode:
            showMessageBox("messagebox.needinternet.title","messagebox.needinternet.text",self.env)
            return

        path = QFileDialog.getSaveFileName(self,self.env.translate("skintab.filepicker.download.title"),os.path.join(QDir.homePath(),"Skin.png"),self.env.translate("skintab.filepicker.filetype.png"))
        
        if path[0]:
            if os.path.isfile(path[0]):
                os.remove(path[0])
            urllib.request.urlretrieve("https://minotar.net/skin/" + self.env.account["uuid"],path[0])

class AboutTab(QWidget):
    def __init__(self,env):
        super().__init__()
        self.titleLabel = QLabel(env.translate("abouttab.label.title") % env.launcherVersion)
        self.fanmadeLabel = QLabel(env.translate("abouttab.label.fanmade"))
        self.dependencyLabel = QLabel(env.translate("abouttab.label.dependency"))
        self.licenseLabel = QLabel(env.translate("abouttab.label.license"))
        self.viewSourceButton = QPushButton(env.translate("abouttab.button.viewSource"))

        self.viewSourceButton.clicked.connect(lambda: webbrowser.open("https://gitlab.com/JakobDev/jdMinecraftLauncher"))

        self.titleLabel.setAlignment(Qt.AlignCenter)
        self.fanmadeLabel.setAlignment(Qt.AlignCenter)
        self.dependencyLabel.setAlignment(Qt.AlignCenter)
        self.licenseLabel.setAlignment(Qt.AlignCenter)

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
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.setReadOnly(True)

    def dataReady(self):
        cursor = self.textCursor()
        cursor.movePosition(cursor.End)
        #print(self.process.readAll())
        cursor.insertText(bytes(self.process.readAll()).decode())
        self.moveCursor(cursor.End)

    def procStarted(self):
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

    def executeCommand(self,profile,args):
        self.profile = profile
        self.process = QProcess(self)
        self.process.setWorkingDirectory(self.env.dataPath)
        self.process.start("java",args)#profile.getJavaPath(),args)
        self.process.readyRead.connect(self.dataReady)
        self.process.started.connect(self.procStarted)
        self.process.finished.connect(self.procFinish)

class Tabs(QTabWidget):
    def __init__(self,env,parrent):
        super().__init__()
        QWebEngineProfile.defaultProfile().setHttpAcceptLanguage(QLocale.system().name())
        QWebEngineProfile.defaultProfile().setHttpUserAgent("jdMinecraftLauncher/" + env.launcherVersion)
        webView = QWebEngineView()
        webView.load(QUrl("https://www.minecraft.net"))
        self.addTab(webView,env.translate("mainwindow.tab.news"))
        self.profileEditor = ProfileEditorTab(env,parrent)
        self.addTab(self.profileEditor,env.translate("mainwindow.tab.profileEditor"))
        self.versionTab = VersionEditorTab(env)
        self.addTab(self.versionTab,env.translate("mainwindow.tab.versionEditor"))
        self.skin = SkinTab(env)
        self.addTab(self.skin,env.translate("mainwindow.tab.skin"))
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

        self.newProfileButton.clicked.connect(self.newProfileButtonClicked)
        self.editProfileButton.clicked.connect(self.editProfileButtonClicked)
        self.playButton.clicked.connect(self.playButtonClicked)
        self.accountButton.clicked.connect(self.logoutButtonClicked)

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
    
    def updateProfilList(self):
        self.profileComboBox.clear()
        for i in self.env.profiles:
            self.profileComboBox.addItem(i.name)
        self.tabWidget.updateProfiles()

    def newProfileButtonClicked(self):
        self.profileWindow.loadProfile(self.env.profiles[self.profileComboBox.currentIndex()],True,True)
        self.profileWindow.show()
        self.profileWindow.setFocus()

    def editProfileButtonClicked(self):
        self.profileWindow.loadProfile(self.env.profiles[self.profileComboBox.currentIndex()],False)
        self.profileWindow.show()
        self.profileWindow.setFocus()
    
    def playButtonClicked(self):
        profile = self.env.profiles[self.profileComboBox.currentIndex()]
        if self.env.offlineMode:
            if os.path.isdir(os.path.join(self.env.dataPath,"versions",profile.getVersionID())):
                self.startMinecraft(profile)
            else:
                showMessageBox("messagebox.installinternet.title","messagebox.installinternet.text",self.env)
        else:
            self.installVersion(profile)
      
    def logoutButtonClicked(self):
        if self.env.offlineMode:
            showMessageBox("messagebox.needinternet.title","messagebox.needinternet.text",self.env)
            return
        if os.path.isfile(os.path.join(self.env.dataPath,"mojang_account.json")):
            os.remove(os.path.join(self.env.dataPath,"mojang_account.json"))
        mojang_api.servers.authserver.invalidate_access_token(self.env.account["accessToken"],self.env.account["clientToken"])
        self.close()
        self.env.loginWindow.show()
        self.env.loginWindow.setFocus()

    def startMinecraft(self,profile):
        args = runMinecraft(self.env.profiles[self.profileComboBox.currentIndex()],self.env)
        o = GameOutputTab(self.env)
        tabid = self.tabWidget.addTab(o,self.env.translate("mainwindow.tab.gameOutput"))
        self.tabWidget.setCurrentIndex(tabid)
        o.executeCommand(profile,args)

    def installFinish(self):
        self.env.updateInstalledVersions()
        self.tabWidget.versionTab.updateVersions()
        self.startMinecraft(self.env.current_running_profile)

    def installVersion(self,profile):
        self.env.current_running_profile = profile
        self.playButton.setEnabled(False)
        self.installThread.setup(profile)
        self.installThread.start()


    def updateAccountInformation(self):
        self.accountLabel.setText(self.env.translate("mainwindow.label.account") % self.env.account["name"])
        self.tabWidget.skin.updateSkin()
        if self.env.offlineMode:
            self.playButton.setText(self.env.translate("mainwindow.button.playOffline"))
        else:
            self.env.translate("mainwindow.button.play")
