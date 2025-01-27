from ...Functions import isFlatpak, selectComboBoxData, isWayland
from ...Constants import DisplayServerSetting, NewsTypeSetting
from PyQt6.QtWidgets import QWidget, QMessageBox, QFileDialog
from ...ui_compiled.OptionsTab import Ui_OptionsTab
from PyQt6.QtCore import Qt, QCoreApplication
from ...Languages import getLanguageNames
from typing import TYPE_CHECKING
import minecraft_launcher_lib
import os


if TYPE_CHECKING:
    from ...Environment import Environment
    from .MainWindow import MainWindow


class OptionsTab(QWidget, Ui_OptionsTab):
    def __init__(self, env: "Environment", parent: "MainWindow") -> None:
        super().__init__()

        self.setupUi(self)

        self._env = env
        self._parent = parent

        languageNames = getLanguageNames()
        self.languageComboBox.addItem(languageNames.get("en", "en"), "en")
        for i in os.listdir(os.path.join(env.currentDir, "translations")):
            if not i.endswith(".qm"):
                continue

            lang = i.removeprefix("jdMinecraftLauncher_").removesuffix(".qm")
            self.languageComboBox.addItem(languageNames.get(lang, lang), lang)
        self.languageComboBox.model().sort(0, Qt.SortOrder.AscendingOrder)
        self.languageComboBox.insertItem(0, QCoreApplication.translate("OptionsTab", "Use System Language"), "default")

        self.displayServerBox.addItem(QCoreApplication.translate("OptionsTab", "Auto"), DisplayServerSetting.AUTO)
        self.displayServerBox.addItem(QCoreApplication.translate("OptionsTab", "Wayland"), DisplayServerSetting.WAYLAND)
        self.displayServerBox.addItem(QCoreApplication.translate("OptionsTab", "XWayland"), DisplayServerSetting.XWAYLAND)

        selectComboBoxData(self.languageComboBox, env.settings.get("language"))

        match env.settings.get("newsType"):
            case NewsTypeSetting.MINECRAFT:
                self.newsMinecraftButton.setChecked(True)
            case NewsTypeSetting.RSS:
                self.newsRssFeedButton.setChecked(True)
            case NewsTypeSetting.WEBSITE:
                self.newsWebsiteButton.setChecked(True)

        self._updateNewsEnabled()
        self.newsFeedUrlEdit.setText(env.settings.get("newsFeedURL"))
        self.newsFeedDefaultBrowserCheckBox.setChecked(env.settings.get("newsFeedDefaultBrowser"))
        self.newsUrlEdit.setText(env.settings.get("newsURL"))
        self.allowMultiLaunchCheckBox.setChecked(self._env.settings.get("enableMultiLaunch"))
        self.extractNativesCheckBox.setChecked(self._env.settings.get("extractNatives"))
        self.windowIconProgressCheckBox.setChecked(self._env.settings.get("windowIconProgress"))
        self.flatpakSubsandboxCheckBox.setChecked(self._env.settings.get("useFlatpakSubsandbox"))
        self.checkUpdatesStartupCheckBox.setChecked(self._env.settings.get("checkUpdatesStartup"))
        selectComboBoxData(self.displayServerBox, self._env.settings.get("displayServer"))

        self.windowIconProgressCheckBox.setVisible(parent.windowIconProgress.isSupported())

        if not isFlatpak():
            self.flatpakSubsandboxCheckBox.setVisible(False)

        self.checkUpdatesStartupCheckBox.setVisible(env.enableUpdater)
        self.displayServerLabel.setVisible(isWayland())
        self.displayServerBox.setVisible(isWayland())

        self.newsMinecraftButton.toggled.connect(self._newsTypeChanged)
        self.newsRssFeedButton.toggled.connect(self._newsTypeChanged)
        self.newsFeedUrlEdit.editingFinished.connect(self._newsFeedUrlChanged)
        self.newsFeedDefaultBrowserCheckBox.stateChanged.connect(self._newsFeedDefaultBrowserCheckBoxChanged)
        self.newsUrlEdit.editingFinished.connect(self._newsUrlChanged)
        self.allowMultiLaunchCheckBox.stateChanged.connect(self._multiLaunchCheckBoxChanged)
        self.extractNativesCheckBox.stateChanged.connect(self._extractNativesCheckBoxChanged)
        self.windowIconProgressCheckBox.stateChanged.connect(self._windowIconProgressCheckBoxChanged)
        self.flatpakSubsandboxCheckBox.stateChanged.connect(self._flatpakSubsandboxCheckBoxChanged)
        self.minecraftDirChangeButton.clicked.connect(self._minecraftDirChangeButtonClicked)
        self.minecraftDirResetButton.clicked.connect(self._minecraftDirResetButtonClicked)
        self.displayServerBox.currentIndexChanged.connect(self._displayServerBoxChanged)

        self._updateMinecraftDirWidgets()

    def _getSelectedNewsType(self) -> str:
        if self.newsMinecraftButton.isChecked():
            return NewsTypeSetting.MINECRAFT
        elif self.newsRssFeedButton.isChecked():
            return NewsTypeSetting.RSS
        elif self.newsWebsiteButton.isChecked():
            return NewsTypeSetting.WEBSITE
        else:
            raise Exception("unknown news type")

    def _updateNewsEnabled(self) -> None:
        newsType = self._getSelectedNewsType()

        self.newsFeedUrlLabel.setEnabled(newsType == NewsTypeSetting.RSS)
        self.newsFeedUrlEdit.setEnabled(newsType == NewsTypeSetting.RSS)
        self.newsUrlLabel.setEnabled(newsType == NewsTypeSetting.WEBSITE)
        self.newsUrlEdit.setEnabled(newsType == NewsTypeSetting.WEBSITE)

    def _newsTypeChanged(self) -> None:
        self._env.settings.set("newsType", self._getSelectedNewsType())

        self._updateNewsEnabled()
        self._parent.updateNewsTab()

    def _newsFeedUrlChanged(self) -> None:
        self._env.settings.set("newsFeedURL", self.newsFeedUrlEdit.text())
        self._parent.updateNewsTab()

    def _newsFeedDefaultBrowserCheckBoxChanged(self) -> None:
        self._env.settings.set("newsFeedDefaultBrowser", self.newsFeedDefaultBrowserCheckBox.isChecked())

    def _newsUrlChanged(self) -> None:
        self._env.settings.set("newsURL", self.newsUrlEdit.text())
        self._parent.updateNewsTab()

    def _multiLaunchCheckBoxChanged(self) -> None:
        self._env.settings.set("enableMultiLaunch", self.allowMultiLaunchCheckBox.isChecked())

    def _extractNativesCheckBoxChanged(self) -> None:
        self._env.settings.set("extractNatives", self.extractNativesCheckBox.isChecked())

    def _windowIconProgressCheckBoxChanged(self) -> None:
        checked = self.windowIconProgressCheckBox.isChecked()
        self._env.settings.set("windowIconProgress", checked)
        if not checked:
            self._parent.windowIconProgress.hide()

    def _flatpakSubsandboxCheckBoxChanged(self) -> None:
        self._env.settings.set("useFlatpakSubsandbox", self.flatpakSubsandboxCheckBox.isChecked())

    def _displayServerBoxChanged(self) -> None:
        self._env.settings.set("displayServer", self.displayServerBox.currentData())

    def _updateMinecraftDirWidgets(self) -> None:
        if (customMinecraftDir := self._env.settings.get("customMinecraftDir")) is not None:
            self.minecraftDirPathButton.setText(customMinecraftDir)
        else:
            self.minecraftDirPathButton.setText(minecraft_launcher_lib.utils.get_minecraft_directory())

        self.minecraftDirResetButton.setEnabled(self._env.settings.get("customMinecraftDir") is not None)

    def _minecraftDirChangeButtonClicked(self) -> None:
        text = QCoreApplication.translate("OptionsTab", "This will change your Minecraft directory.") + "<br><br>"
        text += QCoreApplication.translate("OptionsTab", "This is the directory where Minecraft is installed.") + "<br><br>"
        text += QCoreApplication.translate("OptionsTab", "If you don't set a game directory for your profile, Minecraft will also save its data (saves, options, etc.) there.") + "<br><br>"
        text += QCoreApplication.translate("OptionsTab", "Would you like to proceed?")

        if QMessageBox.question(self, QCoreApplication.translate("OptionsTab", "Change Minecraft directory"), text, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
            return

        path = QFileDialog.getExistingDirectory(self)

        if path == "":
            return

        self._env.minecraftDir = path

        self._env.updateInstalledVersions()
        self._parent.updateProfileList()

        self._env.settings.set("customMinecraftDir", path)

        if not self._env.args.dont_save_data:
            self._env.settings.save(os.path.join(self._env.dataDir, "settings.json"))

        self._updateMinecraftDirWidgets()

    def _minecraftDirResetButtonClicked(self) -> None:
        if QMessageBox.question(self, QCoreApplication.translate("OptionsTab", "Reset Minecraft directory"), QCoreApplication.translate("OptionsTab", "Would you like to reset your Minecraft directory to its default location?"), QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
            return

        self._env.minecraftDir = minecraft_launcher_lib.utils.get_minecraft_directory()

        self._env.updateInstalledVersions()
        self._parent.updateProfileList()

        self._env.settings.set("customMinecraftDir", None)

        if not self._env.args.dont_save_data:
            self._env.settings.save(os.path.join(self._env.dataDir, "settings.json"))

        self._updateMinecraftDirWidgets()

    def saveSettings(self) -> None:
        self._env.settings.set("language", self.languageComboBox.currentData())

        if self.newsMinecraftButton.isChecked():
            self._env.settings.set("newsType", NewsTypeSetting.MINECRAFT)
        elif self.newsRssFeedButton.isChecked():
            self._env.settings.set("newsType", NewsTypeSetting.RSS)
        elif self.newsWebsiteButton.isChecked():
            self._env.settings.set("newsType", NewsTypeSetting.WEBSITE)

        self._env.settings.set("newsFeedURL", self.newsFeedUrlEdit.text())
        self._env.settings.set("newsURL", self.newsUrlEdit.text())
        self._env.settings.set("newsFeedDefaultBrowser", self.newsFeedDefaultBrowserCheckBox.isChecked())
        self._env.settings.set("enableMultiLaunch", self.allowMultiLaunchCheckBox.isChecked())
        self._env.settings.set("extractNatives", self.extractNativesCheckBox.isChecked())
        self._env.settings.set("useFlatpakSubsandbox", self.flatpakSubsandboxCheckBox.isChecked())
        self._env.settings.set("checkUpdatesStartup", self.checkUpdatesStartupCheckBox.isChecked())
        self._env.settings.set("displayServer", self.displayServerBox.currentData())
        self._env.settings.save(os.path.join(self._env.dataDir, "settings.json"))
