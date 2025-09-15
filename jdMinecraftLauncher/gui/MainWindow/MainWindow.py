from jdMinecraftLauncher.utils.WindowIconProgress import createWindowIconProgress
from ...core.ProfileCollection import ProfileCollection
from ...core.VersionCollection import VersionCollection
from ...ui_compiled.MainWindow import Ui_MainWindow
from PyQt6.QtWebEngineCore import QWebEngineProfile
from ...core.AccountManager import AccountManager
from PyQt6.QtCore import QCoreApplication, QEvent
from PyQt6.QtWidgets import QWidget, QMessageBox
from ...utils.InstallMrpack import installMrpack
from ...core.AccountManager import AccountBase
from .ProfileEditorTab import ProfileEditorTab
from .VersionEditorTab import VersionEditorTab
from ...InstallThread import InstallThread
from ..ProfileWindow import ProfileWindow
from .GameOutputTab import GameOutputTab
from .ModLoaderTab import ModLoaderTab
from typing import cast, TYPE_CHECKING
from PyQt6.QtGui import QCloseEvent
from .OptionsTab import OptionsTab
from .AccountTab import AccountTab
from .ModpackTab import ModpackTab
from ...Settings import Settings
from ...Globals import Globals
from .AboutTab import AboutTab
from .NewsTab import NewsTab
import urllib.parse
import traceback
import platform
import sys
import os


if TYPE_CHECKING:
    from ...Profile import Profile


class MainWindow(QWidget, Ui_MainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setupUi(self)

        self.profileListRebuild = False
        self.profileWindow = ProfileWindow(self)
        self.windowIconProgress = createWindowIconProgress(self)

        self.windowIconProgress.hide()

        self.tabWidget.clear()

        QWebEngineProfile.defaultProfile().setHttpAcceptLanguage(Globals.locale.name())
        QWebEngineProfile.defaultProfile().setHttpUserAgent(f"jdMinecraftLauncher/{Globals.launcherVersion}")

        self._newsTab = NewsTab()
        self._newsTab.updateNews()

        self._installThread = InstallThread.getInstance()
        self._profileCollection = ProfileCollection.getInstance()

        self._profileEditorTab = ProfileEditorTab(self)
        self._versionEditorTab = VersionEditorTab()
        self._optionsTab = OptionsTab(self)
        self._modLoaderTab = ModLoaderTab()
        self._modpackTab = ModpackTab(self)
        self._accountTab = AccountTab(self)
        self._aboutTab = AboutTab()

        self.tabWidget.addTab(self._newsTab, QCoreApplication.translate("MainWindow", "News"))
        self.tabWidget.addTab(self._profileEditorTab, QCoreApplication.translate("MainWindow", "Profile Editor"))
        self.tabWidget.addTab(self._versionEditorTab, QCoreApplication.translate("MainWindow", "Version Editor"))
        self.tabWidget.addTab(self._optionsTab, QCoreApplication.translate("MainWindow", "Options"))
        self.tabWidget.addTab(self._modLoaderTab, QCoreApplication.translate("MainWindow", "Install mod loader"))
        self.tabWidget.addTab(self._modpackTab, QCoreApplication.translate("MainWindow", "Install modpack"))
        self.tabWidget.addTab(self._accountTab, QCoreApplication.translate("MainWindow", "Accounts"))
        self.tabWidget.addTab(self._aboutTab, QCoreApplication.translate("MainWindow", "About"))

        self._updateProfileList()

        self.newProfileButton.clicked.connect(self.newProfileButtonClicked)
        self.editProfileButton.clicked.connect(self.editProfileButtonClicked)
        self.playButton.clicked.connect(self.playButtonClicked)
        self.accountButton.clicked.connect(self.logoutButtonClicked)
        self.profileComboBox.currentIndexChanged.connect(self.profileComboBoxIndexChanged)

        self._installThread.text.connect(lambda text: self.progressBar.setFormat(text))
        self._installThread.progress.connect(self.updateProgress)
        self._installThread.progressMax.connect(lambda progress_max: self.progressBar.setMaximum(progress_max))
        self._installThread.started.connect(lambda: self.playButton.setEnabled(False))
        self._installThread.finished.connect(self.installFinish)

        self._profileCollection.profilesChanged.connect(self._updateProfileList)

        self._isFirstOpen = False

    def openMainWindow(self, launchProfile: str | None, url: str | None) -> None:
        if self._isFirstOpen:
            self.show()
            return

        if platform.system() == "Linux":
            from jdMinecraftLauncher.DBusService import DBusService
            DBusService(self)

        if launchProfile:
            profile = self._profileCollection.getProfileByName(launchProfile)
            if profile:
                self.launchProfile(profile)
            else:
                QMessageBox.critical(self, QCoreApplication.translate("MainWindow", "Profile not found"), QCoreApplication.translate("MainWindow", "The given Profile was not found"))
        elif url:
            self.openURL(url)

        self._isFirstOpen = True
        self.show()

        if (loadError := self._profileCollection.getLoadError()) is not None:
            msgBox = QMessageBox()
            msgBox.setWindowTitle(QCoreApplication.translate("MainWindow", "Unable to load Profiles"))
            msgBox.setText(QCoreApplication.translate("MainWindow", "jdMinecraft was unable to load your profiles due to an error. Apologies for any inconvenience. Please report this bug."))
            msgBox.setDetailedText(loadError)
            msgBox.exec()

        if (loadError := Settings.getInstance().getLoadError()) is not None:
            msgBox = QMessageBox()
            msgBox.setWindowTitle(QCoreApplication.translate("MainWindow", "Unable to load Settings"))
            msgBox.setText(QCoreApplication.translate("MainWindow", "jdMinecraft was unable to load your settings due to an error. Apologies for any inconvenience. Please report this bug."))
            msgBox.setDetailedText(loadError)
            msgBox.exec()

    def updateNewsTab(self) -> None:
        self._newsTab.updateNews()

    def openURL(self, url: str) -> None:
        parse_results = urllib.parse.urlparse(url)
        match parse_results.scheme:
            case "jdminecraftlauncher":
                self._handleCustomURL(parse_results.path)
            case "file":
                self._handleOpenPath(parse_results.path)
            case _:
                print(f"Unknown schema: {parse_results.scheme}", file=sys.stderr)

    def _handleCustomURL(self, args: str) -> None:
        try:
            method, param = args.split("/", 1)
        except ValueError:
            return

        match method:
            case "LaunchProfileByID":
                profile = self._profileCollection.getProfileByID(param)
                if profile:
                    self.launchProfile(profile)
                else:
                    QMessageBox.critical(
                        self,
                        QCoreApplication.translate("MainWindow", "Profile not found"),
                        QCoreApplication.translate("MainWindow", "The given Profile was not found")
                    )
            case "LaunchProfileByName":
                profile = self._profileCollection.getProfileByName(param)
                if profile:
                    self.launchProfile(profile)
                else:
                    QMessageBox.critical(
                        self,
                        QCoreApplication.translate("MainWindow", "Profile not found"),
                        QCoreApplication.translate("MainWindow", "The given Profile was not found")
                    )

    def _handleOpenPath(self, path: str) -> None:
        if not os.path.exists(path):
            QMessageBox.critical(
                self,
                QCoreApplication.translate("MainWindow", "File not found"),
                QCoreApplication.translate("MainWindow", "{{path}} was not found").replace("{{path}}", path),
            )
            return

        _, ext = os.path.splitext(path)
        if ext != ".mrpack":
            QMessageBox.critical(
                self,
                QCoreApplication.translate("MainWindow", "Could not open file"),
                QCoreApplication.translate("MainWindow", "{{path}} is not a supported file format").replace("{{path}}", path),
            )
            return

        installMrpack(self, path)

    def _updateProfileList(self) -> None:
        currentIndex = 0
        self.profileListRebuild = True
        self.profileComboBox.clear()

        selectedProfile = self._profileCollection.getSelectedProfile()
        for count, profile in enumerate(self._profileCollection.getProfileList()):
            self.profileComboBox.addItem(profile.name)
            if profile.id == selectedProfile.id:
                currentIndex = count

        self.profileComboBox.setCurrentIndex(currentIndex)
        self.profileListRebuild = False

    def profileComboBoxIndexChanged(self, index: int) -> None:
        if self.profileListRebuild:
            return

        self._profileCollection.setSelectedProfile(self._profileCollection.getProfileList()[index])

    def newProfileButtonClicked(self) -> None:
        self.profileWindow.loadProfile(self._profileCollection.getSelectedProfile(), True, True)
        self.profileWindow.open()

    def editProfileButtonClicked(self) -> None:
        self.profileWindow.loadProfile(self._profileCollection.getSelectedProfile(), False)
        self.profileWindow.open()

    def launchProfile(self, profile: "Profile") -> None:
        if Globals.offlineMode:
            if os.path.isdir(os.path.join(Globals.minecraftDir, "versions", profile.getVersionID())):
                self.startMinecraft(profile)
            else:
                QMessageBox.critical(self, QCoreApplication.translate("MainWindow", "No Internet Connection"), QCoreApplication.translate("MainWindow", "You need a internet connection to install a new version, but you are still able to play already installed versions."))
        else:
            self.installVersion(profile)

    def playButtonClicked(self) -> None:
        self.launchProfile(ProfileCollection.getInstance().getSelectedProfile())

    def logoutButtonClicked(self) -> None:
        if Globals.offlineMode:
            QMessageBox.critical(self, QCoreApplication.translate("MainWindow", "No Internet Connection"), QCoreApplication.translate("MainWindow", "This Feature needs a internet connection"))
            return

        accountManager = AccountManager.getInstance()

        accountManager.removeAccount(cast(AccountBase, accountManager.getSelectedAccount()))

        if accountManager.getSelectedAccount() is None:
            self.hide()
            if accountManager.addMicrosoftAccount(self) is None:
                self.close()
                return
            self.show()

        self.updateAccountInformation()

    def startMinecraft(self, profile: "Profile") -> None:
        try:
            os.makedirs(profile.getGameDirectoryPath())
        except FileExistsError:
            pass
        except Exception:
            print(traceback.format_exc(), file=sys.stderr)
            QMessageBox.critical(
                self,
                QCoreApplication.translate("MainWindow", "Could not create game directory"),
                QCoreApplication.translate("MainWindow", "jdMinecraftLauncher was unable to create {{path}}").replace("{{path}}", profile.getGameDirectoryPath()),
            )
            self.playButton.setEnabled(True)
            return

        outputTab = GameOutputTab(self, self._profileCollection.getSelectedProfile())
        tabID = self.tabWidget.addTab(outputTab, QCoreApplication.translate("MainWindow", "Game Output"))
        self.tabWidget.setCurrentIndex(tabID)
        outputTab.start()

    def installFinish(self) -> None:
        self.windowIconProgress.hide()

        if self._installThread.isVersionNotFound():
            QMessageBox.critical(self, QCoreApplication.translate("MainWindow", "Version not found"), QCoreApplication.translate("MainWindow", "The version used by this profile was not found and could not be installed. Perhaps you have uninstalled it."))
            return

        if self._installThread.getError() is not None:
            text = QCoreApplication.translate("MainWindow", "Due to an error, the installation could not be completed") + "<br><br>"
            text += QCoreApplication.translate("MainWindow", "This may have been caused by a network error")

            msgBox = QMessageBox()
            msgBox.setWindowTitle(QCoreApplication.translate("MainWindow", "Installation failed"))
            msgBox.setText(text)
            msgBox.setDetailedText(self._installThread.getError())
            msgBox.exec()

            self.progressBar.setValue(0)
            self.progressBar.setFormat("")
            self.playButton.setEnabled(True)

            return

        VersionCollection().getInstance().updateVersions()

        if self._installThread.shouldStartMinecraft() and self._installThread.getError() is None:
            self.startMinecraft(self._current_running_profile)
        else:
            self.profileWindow.updateVersionsList()
            self.playButton.setEnabled(True)

    def installVersion(self, profile: "Profile") -> None:
        self._current_running_profile = profile
        self._installThread.setupVanilla(profile)
        self._installThread.start()

    def updateAccountInformation(self) -> None:
        self.accountLabel.setText(QCoreApplication.translate("MainWindow", "Welcome, {{name}}").replace("{{name}}", AccountManager.getInstance().getSelectedAccount().getName()))

        if Globals.offlineMode:
            self.playButton.setText(QCoreApplication.translate("MainWindow", "Play Offline"))
        else:
            self.playButton.setText(QCoreApplication.translate("MainWindow", "Play"))

        self._accountTab.updateAccountTable()

    def updateProgress(self, progress: int) -> None:
        self.progressBar.setValue(progress)

        if Settings.getInstance().get("windowIconProgress"):
            self.windowIconProgress.setProgress(progress / self.progressBar.maximum())

    def event(self, event: QEvent) -> bool:  # type: ignore
        if event.type() == QEvent.Type.WinIdChange:
            self.windowIconProgress = createWindowIconProgress(self)

        return super().event(event)

    def closeEvent(self, event: QCloseEvent) -> None:  # type: ignore
        self._optionsTab.saveSettings()
        self._profileCollection.save()

        event.accept()
        sys.exit(0)
