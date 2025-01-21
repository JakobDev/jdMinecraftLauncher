from jdMinecraftLauncher.ProfileCollection import ProfileCollection
from jdMinecraftLauncher.Settings import Settings
from jdMinecraftLauncher.Profile import Profile
from .AccountManager import AccountManager
from PyQt6.QtWidgets import QApplication
from .Functions import isFlatpak
from PyQt6.QtCore import QLocale
from PyQt6.QtGui import QIcon
import minecraft_launcher_lib
from pathlib import Path
from typing import cast
import argparse
import platform
import requests
import tomllib
import json
import os


class Environment:
    def __init__(self, app: QApplication) -> None:
        self.offlineMode = False
        self.currentDir = os.path.dirname(os.path.realpath(__file__))

        with open(os.path.join(self.currentDir, "version.txt"), "r", encoding="utf-8") as f:
            self.launcherVersion = f.read().strip()

        self.icon = QIcon(os.path.join(self.currentDir, "Icon.svg"))
        self.app = app

        parser = argparse.ArgumentParser()
        parser.add_argument("url", nargs="?")
        parser.add_argument("--minecraft-dir", help="Set the Minecraft Directory")
        parser.add_argument("--data-dir", help="Set the Data Directory")
        parser.add_argument("--launch-profile", help="Launch a Profile")
        parser.add_argument("--account", help="Launch with the selected Account")
        parser.add_argument("--offline-mode", help="Force offline Mode", action="store_true")
        parser.add_argument("--force-start", help="Forces the start on unsupported Platforms", action="store_true")
        parser.add_argument("--dont-save-data", help="Don't save data to the disk (only for development usage)", action="store_true")
        parser.add_argument("--debug", help="Start in Debug Mode", action="store_true")
        self.args = parser.parse_known_args()[0]

        if self.args.data_dir:
            self.dataDir = self.args.data_dir
        else:
            self.dataDir = self.getDataPath()

        if not os.path.exists(self.dataDir):
            os.makedirs(self.dataDir)

        self.debugMode = bool(self.args.debug)

        self.settings = Settings()
        self.settings.load(os.path.join(self.dataDir, "settings.json"))

        if self.args.minecraft_dir:
            self.minecraftDir = self.args.minecraft_dir
        elif self.settings.get("customMinecraftDir") is not None:
            self.minecraftDir = self.settings.get("customMinecraftDir")
        else:
            self.minecraftDir = minecraft_launcher_lib.utils.get_minecraft_directory()

        self.accountManager = AccountManager(self)

        self.profileCollection = ProfileCollection(self)
        self.profileCollection.loadProfiles()

        self.profiles: list[Profile] = []
        self.selectedProfile = 0

        with open(os.path.join(self.currentDir, "Distribution.toml"), "rb") as f:
            distributionConfig = tomllib.load(f)

        self.enableUpdater = not isFlatpak() and distributionConfig.get("EnableUpdater", True)

        if self.settings.get("language") == "default":
            self.locale = QLocale()
        else:
            self.locale = QLocale(self.settings.get("language"))

        if os.path.isdir(self.dataDir):
            self.firstLaunch = False
        else:
            self.firstLaunch = True

    def _getSystemDataDir(self) -> str:
        match platform.system():
            case "Windows":
                return cast(str, os.getenv("APPDATA"))
            case "Darwin":
                return os.path.join(Path.home(), "Library", "Application Support")
            case "Haiku":
                return os.path.join(Path.home(), "config", "settings")
            case _:
                if os.getenv("XDG_DATA_HOME"):
                    return cast(str, os.getenv("XDG_DATA_HOME"))
                else:
                    return os.path.join(Path.home(), ".local", "share")

    def getDataPath(self) -> str:
        if os.path.isdir(os.path.join(minecraft_launcher_lib.utils.get_minecraft_directory(), "jdMinecraftLauncher")):
            return os.path.join(minecraft_launcher_lib.utils.get_minecraft_directory(), "jdMinecraftLauncher")

        dataPath = self._getSystemDataDir()
        if os.path.isdir(os.path.join(dataPath, "jdMinecraftLauncher")):
            return os.path.join(dataPath, "jdMinecraftLauncher")

        return os.path.join(dataPath, "JakobDev", "jdMinecraftLauncher")

    def loadVersions(self) -> None:
        if not self.offlineMode:
            try:
                r = requests.get("https://launchermeta.mojang.com/mc/game/version_manifest_v2.json")
                f = open(os.path.join(self.dataDir, "versions_cache.json"), "w")
                f.write(r.text)
                f.close()
                r.close()
            except Exception:
                print("Failed to update versions list")
        with open(os.path.join(self.dataDir, "versions_cache.json")) as f:
            self.versions = json.load(f)
        self.updateInstalledVersions()

    def updateInstalledVersions(self) -> None:
        versioncheck = {}
        for v in self.versions["versions"]:
            versioncheck[v["id"]] = True

        self.installedVersion = []
        if os.path.isdir(os.path.join(self.minecraftDir, "versions")):
            for v in os.listdir(os.path.join(self.minecraftDir, "versions")):
                json_path = os.path.join(self.minecraftDir, "versions", v, v + ".json")
                if os.path.isfile(json_path):
                    with open(json_path) as f:
                        try:
                            vinfo = json.load(f)
                        except json.decoder.JSONDecodeError as e:
                            print("Error while parsing " + json_path + ": " + e.args[0])
                            continue

                    tmp = {"id": vinfo["id"], "type": vinfo["type"]}
                    self.installedVersion.append(tmp)

                    if vinfo["id"] not in versioncheck:
                        self.versions["versions"].append(tmp)
