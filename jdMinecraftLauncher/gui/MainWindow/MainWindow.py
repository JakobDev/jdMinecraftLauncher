from jdMinecraftLauncher.utils.WindowIconProgress import createWindowIconProgress
from PyQt6.QtCore import QCoreApplication, QEvent, QUrl, QLocale
from ...ui_compiled.MainWindow import Ui_MainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile
from PyQt6.QtWidgets import QWidget, QMessageBox
from ...RunMinecraft import getMinecraftCommand
from .ProfileEditorTab import ProfileEditorTab
from .VersionEditorTab import VersionEditorTab
from ...InstallThread import InstallThread
from ..ProfileWindow import ProfileWindow
from .GameOutputTab import GameOutputTab
from PyQt6.QtGui import QCloseEvent
from .OptionsTab import OptionsTab
from .AccountTab import AccountTab
from typing import TYPE_CHECKING
from .FabricTab import FabricTab
from .ForgeTab import ForgeTab
from .AboutTab import AboutTab
import urllib.parse
import platform
import json
import sys
import os


if TYPE_CHECKING:
    from ...Environment import Environment
    from ...Profile import Profile


class MainWindow(QWidget, Ui_MainWindow):
    def __init__(self, env: "Environment"):
        super().__init__()

        self.setupUi(self)

        self.env = env
        self.profileListRebuild = False
        self.profileWindow = ProfileWindow(self.env,self)
        self.windowIconProgress = createWindowIconProgress(self)

        self.tabWidget.clear()

        QWebEngineProfile.defaultProfile().setHttpAcceptLanguage(QLocale.system().name())
        QWebEngineProfile.defaultProfile().setHttpUserAgent("jdMinecraftLauncher/" + env.launcherVersion)
        newsTab = QWebEngineView()
        newsTab.load(QUrl(env.settings.get("newsURL")))

        self._profileEditorTab = ProfileEditorTab(env, self)
        self._versionEditorTab = VersionEditorTab(env)
        self._optionsTab = OptionsTab(env, self)
        self._forgeTab = ForgeTab(env, self)
        self._fabricTab = FabricTab(env, self)
        self._accountTab = AccountTab(env, self)
        self._aboutTab = AboutTab(env)

        self.tabWidget.addTab(newsTab, QCoreApplication.translate("MainWindow", "News"))
        self.tabWidget.addTab(self._profileEditorTab, QCoreApplication.translate("MainWindow", "Profile Editor"))
        self.tabWidget.addTab(self._versionEditorTab, QCoreApplication.translate("MainWindow", "Version Editor"))
        self.tabWidget.addTab(self._optionsTab, QCoreApplication.translate("MainWindow", "Options"))
        self.tabWidget.addTab(self._forgeTab, QCoreApplication.translate("MainWindow", "Forge"))
        self.tabWidget.addTab(self._fabricTab, QCoreApplication.translate("MainWindow", "Fabric"))
        self.tabWidget.addTab(self._accountTab, QCoreApplication.translate("MainWindow", "Account"))
        self.tabWidget.addTab(self._aboutTab, QCoreApplication.translate("MainWindow", "About"))

        self.newProfileButton.clicked.connect(self.newProfileButtonClicked)
        self.editProfileButton.clicked.connect(self.editProfileButtonClicked)
        self.playButton.clicked.connect(self.playButtonClicked)
        self.accountButton.clicked.connect(self.logoutButtonClicked)
        self.profileComboBox.currentIndexChanged.connect(self.profileComboBoxIndexChanged)

        self.updateProfileList()

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

        if (loadError := self.env.profileCollection.getLoadError()) is not None:
            msgBox = QMessageBox()
            msgBox.setWindowTitle(QCoreApplication.translate("MainWindow", "Unable to load Profiles"))
            msgBox.setText(QCoreApplication.translate("MainWindow", "jdMinecraft was unable to load your profiles due to an error. Apologies for any inconvenience. Please report this bug."))
            msgBox.setDetailedText(loadError)
            msgBox.exec()

        if (loadError := self.env.settings.getLoadError()) is not None:
            msgBox = QMessageBox()
            msgBox.setWindowTitle(QCoreApplication.translate("MainWindow", "Unable to load Settings"))
            msgBox.setText(QCoreApplication.translate("MainWindow", "jdMinecraft was unable to load your settings due to an error. Apologies for any inconvenience. Please report this bug."))
            msgBox.setDetailedText(loadError)
            msgBox.exec()

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

        self._profileEditorTab.updateProfiles()
        self.profileComboBox.setCurrentIndex(currentIndex)
        self.profileListRebuild = False

    def profileComboBoxIndexChanged(self, index: int):
        if not self.profileListRebuild:
            self.env.profileCollection.selectedProfile = self.env.profileCollection.profileList[index].id

    def newProfileButtonClicked(self):
        self.profileWindow.loadProfile(self.env.profileCollection.getSelectedProfile(), True, True)
        self.profileWindow.open()

    def editProfileButtonClicked(self):
        self.profileWindow.loadProfile(self.env.profileCollection.getSelectedProfile(), False)
        self.profileWindow.open()

    def launchProfile(self, profile: "Profile") -> None:
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

        self.env.accountManager.removeAccount(self.env.accountManager.getSelectedAccount())

        if self.env.accountManager.getSelectedAccount() is None:
            self.hide()
            if self.env.accountManager.addMicrosoftAccount(self) is None:
                self.close()
                return
            self.show()

        self.updateAccountInformation()

    def startMinecraft(self, profile: "Profile"):
        if self.env.settings.get("extractNatives"):
            natives_path = os.path.join(tempfile.gettempdir(), "minecraft_natives_" + str(random.randrange(0, 10000000)))
        else:
            natives_path = ""

        args = getMinecraftCommand(self.env.profileCollection.getSelectedProfile(), self.env, natives_path)
        outputTab = GameOutputTab(self.env)
        tabID = self.tabWidget.addTab(outputTab, QCoreApplication.translate("MainWindow", "Game Output"))
        self.tabWidget.setCurrentIndex(tabID)
        outputTab.executeCommand(profile, args, natives_path)

    def installFinish(self) -> None:
        self.windowIconProgress.hide()

        if self.installThread.isVersionNotFound():
            QMessageBox.critical(self, QCoreApplication.translate("MainWindow", "Version not found"), QCoreApplication.translate("MainWindow", "The version used by this profile was not found and could not be installed. Perhaps you have uninstalled it."))
            return

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
            self._versionEditorTab.updateVersions()
            self.startMinecraft(self.env.current_running_profile)
        else:
            self.env.loadVersions()
            self.profileWindow.updateVersionsList()
            self.setInstallButtonsEnabled(True)

    def installVersion(self, profile: "Profile") -> None:
        self.env.current_running_profile = profile
        self.playButton.setEnabled(False)
        self.installThread.setup(profile)
        self.installThread.start()

    def updateAccountInformation(self) -> None:
        self.accountLabel.setText(QCoreApplication.translate("MainWindow", "Welcome, {{name}}").replace("{{name}}", self.env.accountManager.getSelectedAccount().getName()))
        self._profileEditorTab.updateProfiles()

        if self.env.offlineMode:
            self.playButton.setText(QCoreApplication.translate("MainWindow", "Play Offline"))
        else:
            self.playButton.setText(QCoreApplication.translate("MainWindow", "Play"))

        self._accountTab.updateAccountTable()

    def setInstallButtonsEnabled(self, enabled: bool) -> None:
        self.playButton.setEnabled(enabled)
        self._forgeTab.setButtonsEnabled(enabled)
        self._fabricTab.setButtonsEnabled(enabled)

    def updateProgress(self, progress: int) -> None:
        self.progressBar.setValue(progress)

        if self.env.settings.get("windowIconProgress"):
            self.windowIconProgress.setProgress(progress / self.progressBar.maximum())

    def event(self, event: QEvent) -> bool:
        if event.type() == QEvent.Type.WinIdChange:
            self.windowIconProgress = createWindowIconProgress(self)

        return super().event(event)

    def closeEvent(self, event: QCloseEvent) -> None:
        if self.env.args.dont_save_data:
            event.accept()
            sys.exit(0)

        self.env.profileCollection.save()
        self._optionsTab.saveSettings()

        event.accept()
        sys.exit(0)
