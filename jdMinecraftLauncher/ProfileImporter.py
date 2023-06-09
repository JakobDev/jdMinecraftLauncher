from jdMinecraftLauncher.Profile import Profile
from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QMessageBox
from typing import TYPE_CHECKING
import minecraft_launcher_lib
import traceback


if TYPE_CHECKING:
    from jdMinecraftLauncher.Environment import Environment


def _convertProfile(env: "Environment", vanilla_profile: minecraft_launcher_lib.types.VanillaLauncherProfile) -> Profile:
    profile = Profile(vanilla_profile["name"], env)

    profile.useLatestVersion = False
    if vanilla_profile["versionType"] == "latest-release":
        profile.useLatestVersion = True
    elif vanilla_profile["versionType"] == "latest-snapshot":
        profile.useLatestSnapshot = True
        profile.enableSnapshots = True
    else:
        profile.version = vanilla_profile["version"]
        for i in env.versions["versions"]:
            if i["id"] == vanilla_profile["version"]:
                if i["type"] == "old_alpha":
                    profile.enableAlpha = True
                elif i["type"] == "old_beta":
                    profile.enableBeta = True
                elif i["type"] == "snapshot":
                    profile.enableSnapshots = True

    if vanilla_profile.get("gameDirectory") is not None:
        profile.gameDirectoryPath = vanilla_profile["gameDirectory"]
        profile.customGameDirectory = True

    if vanilla_profile.get("customResolution") is not None:
        profile.resolutionY = str(vanilla_profile["customResolution"]["height"])
        profile.resolutionY = str(vanilla_profile["customResolution"]["width"])
        profile.customResolution = True

    if vanilla_profile.get("javaExecutable") is not None:
        profile.executable = vanilla_profile["javaExecutable"]
        profile.customExecutable = True

    if vanilla_profile.get("javaArguments") is not None:
        profile.arguments = " ".join(vanilla_profile["javaArguments"])
        profile.customArguments = True

    return profile


def _importProfiles(env: "Environment") -> list[Profile]:
    profileList = []
    for i in minecraft_launcher_lib.vanilla_launcher.load_vanilla_launcher_profiles(env.minecraftDir):
        profileList.append(_convertProfile(env, i))

    return profileList


def askProfileImport(env: "Environment") -> None:
    if not minecraft_launcher_lib.vanilla_launcher.do_vanilla_launcher_profiles_exists(env.minecraftDir):
        return

    if QMessageBox.question(env.mainWindow, QCoreApplication.translate("ProfileImporter", "Import Profiles"), QCoreApplication.translate("ProfileImporter", "jdMinecraftLauncher can import Profiles from the vanilla Launcher. Do you want to import your Profiles?"), QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
        return

    try:
        profiles = _importProfiles(env)
    except Exception as ex:
        msgBox = QMessageBox()
        msgBox.setWindowTitle(QCoreApplication.translate("ProfileImporter", "Error"))
        msgBox.setText(QCoreApplication.translate("ProfileImporter", "Due to an error, the profiles could not be imported. Sorry for that."))
        msgBox.setDetailedText(traceback.format_exc())
        msgBox.exec()
        return

    for i in profiles:
        env.profileCollection.profileList.append(i)

    env.mainWindow.updateProfileList()