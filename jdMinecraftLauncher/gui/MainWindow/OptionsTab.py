from ...ui_compiled.OptionsTab import Ui_OptionsTab
from PyQt6.QtCore import Qt, QCoreApplication
from ...Languages import getLanguageNames
from PyQt6.QtWidgets import QWidget
from typing import TYPE_CHECKING
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

    def _multiLaunchCheckBoxChanged(self):
        self._env.settings.set("enableMultiLaunch", self.allowMultiLaunchCheckBox.isChecked())

    def _extractNativesCheckBoxChanged(self):
        self._env.settings.set("extractNatives", self.extractNativesCheckBox.isChecked())

    def _windowIconProgressCheckBoxChanged(self) -> None:
        checked = self.windowIconProgressCheckBox.isChecked()
        self._env.settings.set("windowIconProgress", checked)
        if not checked:
            self._parent.windowIconProgress.hide()
