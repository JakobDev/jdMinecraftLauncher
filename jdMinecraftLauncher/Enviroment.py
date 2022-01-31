from jdTranslationHelper import jdTranslationHelper
from jdMinecraftLauncher.Profile import Profile
from jdMinecraftLauncher.Settings import Settings
from jdMinecraftLauncher.Functions import showMessageBox
from jdMinecraftLauncher.MicrosoftSecrets import MicrosoftSecrets
from PyQt6.QtWidgets import QInputDialog, QWidget
from PyQt6.QtCore import QLocale
from PyQt6.QtGui import QIcon
import minecraft_launcher_lib
import requests
import json
import copy
import sys
import os

class Enviroment():
    def __init__(self):
        self.launcherVersion = "3.1"
        self.offlineMode = False
        self.currentDir = os.path.dirname(os.path.realpath(__file__))

        if len(sys.argv) == 2:
            self.dataPath = sys.argv[1]
        else:
            self.dataPath = minecraft_launcher_lib.utils.get_minecraft_directory()

        if not os.path.exists(os.path.join(self.dataPath,"jdMinecraftLauncher")):
            os.makedirs(os.path.join(self.dataPath,"jdMinecraftLauncher"))

        self.secrets = MicrosoftSecrets(self)

        self.settings = Settings(self)

        if self.settings.language == "default":
            self.translations = jdTranslationHelper(lang=QLocale.system().name())
        else:
            self.translations = jdTranslationHelper(lang=self.settings.language)
        self.translations.loadDirectory(os.path.join(self.currentDir,"translation"))

        self.accountList = []
        self.selectedAccount = 0
        self.disableAccountSave = []
        if os.path.isfile(os.path.join(self.dataPath,"jdMinecraftLauncher","microsoft_accounts.json")):
            with open(os.path.join(self.dataPath,"jdMinecraftLauncher","microsoft_accounts.json")) as f:
                data = json.load(f)
                self.accountList = data.get("accountList",[])
                self.selectedAccount = data.get("selectedAccount",0)
                try:
                    self.account = copy.copy(self.accountList[self.selectedAccount])
                except IndexError:
                    self.account = copy.copy(self.accountList[0])
                    self.selectedAccount = 0

        self.loadVersions()

        self.profiles = []
        self.selectedProfile = 0
        if os.path.isfile(os.path.join(self.dataPath,"jdMinecraftLauncher","profiles.json")):
            with open(os.path.join(self.dataPath,"jdMinecraftLauncher","profiles.json")) as f:
                data = json.load(f)
                if isinstance(data,list):
                    profileList = data
                else:
                    profileList = data["profileList"]
                    self.selectedProfile = data["selectedProfile"]
            for i in profileList:
                p = Profile(i["name"],self)
                p.load(i)
                self.profiles.append(p)
        else:
            self.profiles.append(Profile("Default",self))

    def translate(self, string, default=None):
        #Just a litle shortcut
        return self.translations.translate(string,default=default)

    def loadVersions(self):
        if not self.offlineMode:
            try:
                r = requests.get("https://launchermeta.mojang.com/mc/game/version_manifest.json")
                f = open(os.path.join(self.dataPath,"jdMinecraftLauncher","versions_cache.json"),"w")
                f.write(r.text)
                f.close()
                r.close()
            except:
                print("Failed to update versions list")
        with open(os.path.join(self.dataPath,"jdMinecraftLauncher","versions_cache.json")) as f:
            self.versions = json.load(f)
        self.updateInstalledVersions()

    def updateInstalledVersions(self):
        versioncheck = {}
        for v in self.versions["versions"]:
            versioncheck[v["id"]] = True

        self.installedVersion = []
        if os.path.isdir(os.path.join(self.dataPath,"versions")):
            for v in os.listdir(os.path.join(self.dataPath,"versions")):
                json_path = os.path.join(self.dataPath,"versions",v,v + ".json")
                if os.path.isfile(json_path):
                    with open(json_path) as f:
                        try:
                            vinfo = json.load(f)
                        except json.decoder.JSONDecodeError as e:
                            print("Error while parsing " + json_path + ": " + e.args[0])
                            continue
                    tmp = {}
                    tmp["id"] = vinfo["id"]
                    tmp["type"] = vinfo["type"]
                    self.installedVersion.append(tmp)

                    if vinfo["id"] not in versioncheck:
                        self.versions["versions"].append(tmp)

