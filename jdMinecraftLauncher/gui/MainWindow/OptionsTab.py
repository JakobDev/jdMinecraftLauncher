from ...ui_compiled.OptionsTab import Ui_OptionsTab
from PyQt6.QtCore import Qt, QCoreApplication
from ...Languages import getLanguageNames
from PyQt6.QtWidgets import QWidget, QMessageBox, QFileDialog
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

        for i in range(self.languageComboBox.count()):
            if self.languageComboBox.itemData(i) == env.settings.get("language"):
                self.languageComboBox.setCurrentIndex(i)

        self.urlEdit.setText(env.settings.get("newsURL"))
        self.allowMultiLaunchCheckBox.setChecked(self._env.settings.get("enableMultiLaunch"))
        self.extractNativesCheckBox.setChecked(self._env.settings.get("extractNatives"))
        self.windowIconProgressCheckBox.setChecked(self._env.settings.get("windowIconProgress"))

        self.windowIconProgressCheckBox.setVisible(parent.windowIconProgress.isSupported())

        self.allowMultiLaunchCheckBox.stateChanged.connect(self._multiLaunchCheckBoxChanged)
        self.extractNativesCheckBox.stateChanged.connect(self._extractNativesCheckBoxChanged)
        self.windowIconProgressCheckBox.stateChanged.connect(self._windowIconProgressCheckBoxChanged)
        self.minecraftDirChangeButton.clicked.connect(self._minecraftDirChangeButtonClicked)
        self.minecraftDirResetButton.clicked.connect(self._minecraftDirResetButtonClicked)

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

    def _updateMinecraftDirWidgets(self) -> None:
        if (customMinecraftDir := self._env.settings.get("customMinecraftDir")) is not None:
            self.minecraftDirPathButton.setText(customMinecraftDir)
        else:
            self.minecraftDirPathButton.setText(minecraft_launcher_lib.utils.get_minecraft_directory())

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
        self._env.settings.save(os.path.join(self._env.dataDir, "settings.json"))

        self._updateMinecraftDirWidgets()

    def _minecraftDirResetButtonClicked(self) -> None:
        if QMessageBox.question(self, QCoreApplication.translate("OptionsTab", "Reset Minecraft directory"), QCoreApplication.translate("OptionsTab", "Would you like to reset your Minecraft directory to its default location?"), QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
            return

        self._env.minecraftDir = minecraft_launcher_lib.utils.get_minecraft_directory()

        self._env.updateInstalledVersions()
        self._parent.updateProfileList()

        self._env.settings.set("customMinecraftDir", None)
        self._env.settings.save(os.path.join(self._env.dataDir, "settings.json"))

        self._updateMinecraftDirWidgets()
