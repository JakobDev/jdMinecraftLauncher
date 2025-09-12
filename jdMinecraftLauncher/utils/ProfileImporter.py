from ..core.ProfileCollection import ProfileCollection
from ..core.VersionCollection import VersionCollection
from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QMessageBox
from typing import TYPE_CHECKING
import minecraft_launcher_lib
from ..Globals import Globals
from ..Profile import Profile
import traceback


if TYPE_CHECKING:
    from jdMinecraftLauncher.gui.MainWindow.MainWindow import MainWindow


def _convertProfile(vanilla_profile: minecraft_launcher_lib.types.VanillaLauncherProfile) -> Profile:
    profile = ProfileCollection.getInstance().createProfile(vanilla_profile["name"])

    profile.useLatestVersion = False
    if vanilla_profile["versionType"] == "latest-release":
        profile.useLatestVersion = True
    elif vanilla_profile["versionType"] == "latest-snapshot":
        profile.useLatestSnapshot = True
        profile.enableSnapshots = True
    else:
        profile.version = vanilla_profile["version"]  # type: ignore
        for version in VersionCollection.getInstance().getVersionList():
            if version["id"] == vanilla_profile["version"]:
                match version["type"]:
                    case "old_alpha":
                        profile.enableAlpha = True
                    case "old_beta":
                        profile.enableBeta = True
                    case "snapshot":
                        profile.enableSnapshots = True

    if vanilla_profile.get("gameDirectory") is not None:
        profile.gameDirectoryPath = vanilla_profile["gameDirectory"]  # type: ignore
        profile.customGameDirectory = True

    if vanilla_profile.get("customResolution") is not None:
        profile.resolutionY = str(vanilla_profile["customResolution"]["height"])  # type: ignore
        profile.resolutionY = str(vanilla_profile["customResolution"]["width"])  # type: ignore
        profile.customResolution = True

    if vanilla_profile.get("javaExecutable") is not None:
        profile.executable = vanilla_profile["javaExecutable"]  # type: ignore
        profile.customExecutable = True

    if vanilla_profile.get("javaArguments") is not None:
        profile.arguments = " ".join(vanilla_profile["javaArguments"])  # type: ignore
        profile.customArguments = True

    return profile


def _importProfiles() -> list[Profile]:
    profileList = []
    for i in minecraft_launcher_lib.vanilla_launcher.load_vanilla_launcher_profiles(Globals.minecraftDir):
        profileList.append(_convertProfile(i))

    return profileList


def askProfileImport(mainWindow: "MainWindow") -> None:
    if not minecraft_launcher_lib.vanilla_launcher.do_vanilla_launcher_profiles_exists(Globals.minecraftDir):
        return

    if QMessageBox.question(mainWindow, QCoreApplication.translate("ProfileImporter", "Import Profiles"), QCoreApplication.translate("ProfileImporter", "jdMinecraftLauncher can import Profiles from the vanilla Launcher. Do you want to import your Profiles?"), QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
        return

    try:
        profiles = _importProfiles()
    except Exception:
        msgBox = QMessageBox(mainWindow)
        msgBox.setWindowTitle(QCoreApplication.translate("ProfileImporter", "Error"))
        msgBox.setText(QCoreApplication.translate("ProfileImporter", "Due to an error, the profiles could not be imported. Sorry for that."))
        msgBox.setDetailedText(traceback.format_exc())
        msgBox.exec()
        return

    profileCollection = ProfileCollection.getInstance()
    for currentProfile in profiles:
        profileCollection.updateProfile(currentProfile)
