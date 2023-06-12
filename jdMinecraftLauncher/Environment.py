from jdMinecraftLauncher.Profile import Profile
from jdMinecraftLauncher.Settings import Settings
from jdMinecraftLauncher.MicrosoftSecrets import MicrosoftSecrets
from jdMinecraftLauncher.ProfileCollection import ProfileCollection
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
import minecraft_launcher_lib
from typing import Optional
from pathlib import Path
import argparse
import platform
import requests
import json
import copy
import sys
import os


class Environment:
    def __init__(self, app: QApplication):
        self.offlineMode = False
        self.currentDir = os.path.dirname(os.path.realpath(__file__))

        with open(os.path.join(self.currentDir, "version.txt"), "r", encoding="utf-8") as f:
            self.launcherVersion = f.read().strip()

        self.icon = QIcon(os.path.join(self.currentDir , "Icon.svg"))
        self.app = app

        parser = argparse.ArgumentParser()
        parser.add_argument("url", nargs="?")
        parser.add_argument("--minecraft-dir", help="Set the Minecraft Directory")
        parser.add_argument("--data-dir", help="Set the Data Directory")
        parser.add_argument("--launch-profile", help="Launch a Profile")
        parser.add_argument("--account", help="Launch with the selected Account")
        parser.add_argument("--offline-mode", help="Force offline Mode", action="store_true")
        parser.add_argument("--force-start", help="Forces the start on unsupported Platforms", action="store_true")
        parser.add_argument("--dont-save-data", help="Don't save data to the disk (only for development usage", action="store_true")
        self.args = parser.parse_known_args()[0]

        if self.args.minecraft_dir:
            self.minecraftDir = self.args.minecraft_dir
        else:
            self.minecraftDir = minecraft_launcher_lib.utils.get_minecraft_directory()

        if self.args.data_dir:
            self.dataDir = self.args.data_dir
        else:
            self.dataDir = self.getDataPath()

        if not os.path.exists(self.minecraftDir):
            os.makedirs(self.minecraftDir)

        if not os.path.exists(self.dataDir):
            os.makedirs(self.dataDir)

        self.secrets = MicrosoftSecrets(self)

        self.settings = Settings()
        self.settings.load(os.path.join(self.dataDir, "settings.json"))

        self.accountList = []
        self.selectedAccount = 0
        self.disableAccountSave = []
        if os.path.isfile(os.path.join(self.dataDir, "microsoft_accounts.json")):
            with open(os.path.join(self.dataDir, "microsoft_accounts.json")) as f:
                data = json.load(f)
                self.accountList = data.get("accountList",[])
                self.selectedAccount = data.get("selectedAccount",0)
                try:
                    self.account = copy.copy(self.accountList[self.selectedAccount])
                except IndexError:
                    self.account = copy.copy(self.accountList[0])
                    self.selectedAccount = 0

        if self.args.account:
            for count, account in enumerate(self.accountList):
                if self.args.account == account["name"]:
                    self.account = copy.copy(account)
                    self.selectedAccount = count
                    break
            else:
                print(f"Account {self.args.account} was not found", file=sys.stderr)

        self.loadVersions()

        self.profileCollection = ProfileCollection(self)
        self.profileCollection.loadProfiles()

        self.profiles: list[Profile] = []
        self.selectedProfile = 0

        if os.path.isdir(self.dataDir):
            self.firstLaunch = False
        else:
            self.firstLaunch = True

    def getDataPath(self) -> str:
        if os.path.isdir(os.path.join(self.minecraftDir, "jdMinecraftLauncher")):
            return os.path.join(self.minecraftDir, "jdMinecraftLauncher")
        elif platform.system() == "Windows":
            return os.path.join(os.getenv("appdata"), "jdMinecraftLauncher")
        elif platform.system() == "Darwin":
            return os.path.join(str(Path.home()), "Library", "Application Support", "jdMinecraftLauncher")
        elif platform.system() == "Haiku":
            return os.path.join(str(Path.home()), "config", "settings", "jdMinecraftLauncher")
        else:
            if os.getenv("XDG_DATA_HOME"):
                return os.path.join(os.getenv("XDG_DATA_HOME"), "jdMinecraftLauncher")
            else:
                return os.path.join(str(Path.home()), ".local", "share", "jdMinecraftLauncher")

    def loadVersions(self):
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

    def updateInstalledVersions(self):
        versioncheck = {}
        for v in self.versions["versions"]:
            versioncheck[v["id"]] = True

        self.installedVersion = []
        if os.path.isdir(os.path.join(self.minecraftDir,"versions")):
            for v in os.listdir(os.path.join(self.minecraftDir,"versions")):
                json_path = os.path.join(self.minecraftDir,"versions",v,v + ".json")
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
