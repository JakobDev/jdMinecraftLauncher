from PyQt6.QtWidgets import QWidget, QDialog, QScrollArea, QCheckBox, QLabel, QVBoxLayout, QDialogButtonBox, QMessageBox, QInputDialog
from ..core.ProfileCollection import ProfileCollection
from PyQt6.QtCore import Qt, QCoreApplication
from ..InstallThread import InstallThread
from ..Functions import getRealPath
import minecraft_launcher_lib


class OptionalFilesDialog(QDialog):
    def __init__(self, parent: QWidget, optionalFiles: list[str]) -> None:
        super().__init__(parent)

        self._ok = False
        self._checkboxList: list[QCheckBox] = []

        firstLabel = QLabel(QCoreApplication.translate("InstallMrpack", "This Modpacks contains some optional files."))
        firstLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        secondLabel = QLabel(QCoreApplication.translate("InstallMrpack", "Select which of them you want to install."))
        secondLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        scrollLayout = QVBoxLayout()
        for currentFile in optionalFiles:
            checkbox = QCheckBox(currentFile)
            scrollLayout.addWidget(checkbox)

        scrollWidget = QWidget()
        scrollWidget.setLayout(scrollLayout)
        scrollArea = QScrollArea()
        scrollArea.setWidget(scrollWidget)

        buttonBox = QDialogButtonBox()
        buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)

        buttonBox.accepted.connect(self._okButtonClicked)
        buttonBox.rejected.connect(self.close)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(firstLabel)
        mainLayout.addWidget(secondLabel)
        mainLayout.addWidget(scrollArea)
        mainLayout.addWidget(buttonBox)

        self.setLayout(mainLayout)
        self.setWindowTitle(QCoreApplication.translate("InstallMrpack", "Install modpack"))

    def _okButtonClicked(self) -> None:
        self._ok = True
        self.close()

    def getOptionalFiles(self) -> tuple[list[str], bool]:
        self.exec()

        optionalFiles: list[str] = []
        for checkbox in self._checkboxList:
            if checkbox.isChecked():
                optionalFiles.append(checkbox.text())

        return optionalFiles, self._ok


def installMrpack(parent: QWidget, path: str) -> None:
    profileCollection = ProfileCollection.getInstance()

    try:
        info = minecraft_launcher_lib.mrpack.get_mrpack_information(path)
    except Exception:
        QMessageBox.critical(
            parent,
            QCoreApplication.translate("InstallMrpack", "Invalid file"),
            QCoreApplication.translate("InstallMrpack", "{{path}} is not a valid Modrinth modpack").replace("{{path}}", getRealPath(path))
        )
        return

    text = QCoreApplication.translate("InstallMrpack", "This file includes the following Modpack:") + "<br><br>"
    text += QCoreApplication.translate("InstallMrpack", "Name:") + " "
    text += info["name"] + "<br>"

    if info["summary"] != "":
        text += QCoreApplication.translate("InstallMrpack", "Summary:") + " "
        text += info["summary"] + "<br>"

    text += QCoreApplication.translate("InstallMrpack", "Minecraft version:") + " " + info["minecraftVersion"] + "<br><br>"
    text += QCoreApplication.translate("InstallMrpack", "Do you want to install it?")

    if QMessageBox.question(
        parent,
        QCoreApplication.translate("InstallMrpack", "Install modpack"),
        text, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    ) != QMessageBox.StandardButton.Yes:
        return

    nameList: list[str] = []
    for currentProfile in profileCollection.getProfileList():
        nameList.append(currentProfile.name)

    selectedName, ok = QInputDialog.getItem(
        parent,
        QCoreApplication.translate("InstallMrpack", "Install modpack"),
        QCoreApplication.translate("InstallMrpack", "Please select a profile for which you would like to install the modpack"),
        nameList,
        0,
        False
    )

    if not ok:
        return

    selectedProfile = profileCollection.getProfileByName(selectedName)
    assert selectedProfile is not None

    if len(info["optionalFiles"]) == 0:
        optionalFiles: list[str] = []
    else:
        optionalFiles, ok = OptionalFilesDialog(parent, info["optionalFiles"]).getOptionalFiles()
        if not ok:
            return

    installThread = InstallThread.getInstance()
    installThread.setupMrpackInstall(selectedProfile, path, optionalFiles)
    installThread.start()
