from ...Functions import isFlatpak, selectComboBoxData, isWayland
from PyQt6.QtWidgets import QWidget, QMessageBox, QFileDialog
from ...ui_compiled.OptionsTab import Ui_OptionsTab
from PyQt6.QtCore import Qt, QCoreApplication
from ...Constants import DisplayServerSetting
from ...Languages import getLanguageNames
from typing import TYPE_CHECKING
import minecraft_launcher_lib
import os


if TYPE_CHECKING:
    from ...Environment import Environment
    from .MainWindow import MainWindow


class OptionsTab(QWidget, Ui_OptionsTab):
    def __init__(self, env: "Environment", parent: "MainWindow"):
        super().__init__()

        self.setupUi(self)

        self._env = env
        self._parent = parent

        languageNames = getLanguageNames()
        self.languageComboBox.addItem(languageNames.get("en", "en"), "en")
        for i in os.listdir(os.path.join(env.currentDir,"translations")):
            if not i.endswith(".qm"):
                continue

            lang = i.removeprefix("jdMinecraftLauncher_").removesuffix(".qm")
            self.languageComboBox.addItem(languageNames.get(lang, lang), lang)
        self.languageComboBox.model().sort(0, Qt.SortOrder.AscendingOrder)
        self.languageComboBox.insertItem(0, QCoreApplication.translate("OptionsTab", "Use System Language"), "default")

        self.displayServerBox.addItem(QCoreApplication.translate("OptionsTab", "Auto"),DisplayServerSetting.AUTO)
        self.displayServerBox.addItem(QCoreApplication.translate("OptionsTab", "Wayland"),DisplayServerSetting.WAYLAND)
        self.displayServerBox.addItem(QCoreApplication.translate("OptionsTab", "XWayland"),DisplayServerSetting.XWAYLAND)

        selectComboBoxData(self.languageComboBox, env.settings.get("language"))
        self.urlEdit.setText(env.settings.get("newsURL"))
        self.allowMultiLaunchCheckBox.setChecked(self._env.settings.get("enableMultiLaunch"))
        self.extractNativesCheckBox.setChecked(self._env.settings.get("extractNatives"))
        self.windowIconProgressCheckBox.setChecked(self._env.settings.get("windowIconProgress"))
        self.windowIconProgressCheckBox.setChecked(self._env.settings.get("useFlatpakSubsandbox"))
        self.checkUpdatesStartupCheckBox.setChecked(self._env.settings.get("checkUpdatesStartup"))
        selectComboBoxData(self.displayServerBox, self._env.settings.get("displayServer"))

        self.windowIconProgressCheckBox.setVisible(parent.windowIconProgress.isSupported())

        if not isFlatpak():
            self.flatpakSubsandboxCheckBox.setVisible(False)

        self.checkUpdatesStartupCheckBox.setVisible(env.enableUpdater)
        self.displayServerLabel.setVisible(isWayland())
        self.displayServerBox.setVisible(isWayland())

        self.allowMultiLaunchCheckBox.stateChanged.connect(self._multiLaunchCheckBoxChanged)
        self.extractNativesCheckBox.stateChanged.connect(self._extractNativesCheckBoxChanged)
        self.windowIconProgressCheckBox.stateChanged.connect(self._windowIconProgressCheckBoxChanged)
        self.flatpakSubsandboxCheckBox.stateChanged.connect(self._flatpakSubsandboxCheckBoxChanged)
        self.minecraftDirChangeButton.clicked.connect(self._minecraftDirChangeButtonClicked)
        self.minecraftDirResetButton.clicked.connect(self._minecraftDirResetButtonClicked)
        self.displayServerBox.currentIndexChanged.connect(self._displayServerBoxChanged)

        self._updateMinecraftDirWidgets()

    def _multiLaunchCheckBoxChanged(self):
        self._env.settings.set("enableMultiLaunch", self.allowMultiLaunchCheckBox.isChecked())

    def _extractNativesCheckBoxChanged(self):
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
        self._env.settings.set("newsURL", self.urlEdit.text())
        self._env.settings.set("enableMultiLaunch", self.allowMultiLaunchCheckBox.isChecked())
        self._env.settings.set("extractNatives", self.extractNativesCheckBox.isChecked())
        self._env.settings.set("useFlatpakSubsandbox", self.flatpakSubsandboxCheckBox.isChecked())
        self._env.settings.set("checkUpdatesStartup", self.checkUpdatesStartupCheckBox.isChecked())
        self._env.settings.set("displayServer", self.displayServerBox.currentData())
        self._env.settings.save(os.path.join(self._env.dataDir, "settings.json"))
