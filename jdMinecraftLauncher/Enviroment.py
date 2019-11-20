from jdMinecraftLauncher.TranslationHelper import TranslationHelper
from jdMinecraftLauncher.Profile import Profile
from PyQt5.QtCore import QLocale
from PyQt5.QtGui import QIcon
import minecraft_launcher_lib
import requests
import json
import sys
import os

class Enviroment():
    def __init__(self):
        self.launcherVersion = "1.2"
        self.offlineMode = False
        self.currentDir = os.path.dirname(os.path.realpath(__file__))

        if len(sys.argv) == 2:
            self.dataPath = sys.argv[1]
        else:
            self.dataPath = minecraft_launcher_lib.utils.get_minecraft_directory()

        if not os.path.exists(self.dataPath):
            os.makedirs(self.dataPath)

        self.translations = TranslationHelper(QLocale.system().name())

        self.loadVersions()

        self.profiles = []
        if os.path.isfile(os.path.join(self.dataPath,"jdLauncher_profiles.json")):
            with open(os.path.join(self.dataPath,"jdLauncher_profiles.json")) as f:
                data = json.load(f)
            for i in data:
                p = Profile(i["name"],self)
                p.load(i)
                self.profiles.append(p)
        else:
            self.profiles.append(Profile("Default",self))


    def translate(self, string):
        #Just a litle shortcut
        return self.translations.translate(string)

    def loadVersions(self):
        if not self.offlineMode:
            try:
                r = requests.get("https://launchermeta.mojang.com/mc/game/version_manifest.json")
                f = open(os.path.join(self.dataPath,"versions_cache.json"),"w")
                f.write(r.text)
                f.close()
                r.close()
            except:
                print("Failed to update versions list")
        with open(os.path.join(self.dataPath,"versions_cache.json")) as f:
            self.versions = json.load(f)
        self.updateInstalledVersions()

    def updateInstalledVersions(self):
        versioncheck = {}
        for v in self.versions["versions"]:
            versioncheck[v["id"]] = True

        self.installedVersion = []
        if os.path.isdir(os.path.join(self.dataPath,"versions")):
            for v in os.listdir(os.path.join(self.dataPath,"versions")):
                if os.path.isfile(os.path.join(self.dataPath,"versions",v,v + ".json")):
                    with open(os.path.join(self.dataPath,"versions",v,v + ".json")) as f:
                        vinfo = json.load(f)
                    tmp = {}
                    tmp["id"] = vinfo["id"]
                    tmp["type"] = vinfo["type"]
                    self.installedVersion.append(tmp)

                    if vinfo["id"] not in versioncheck:
                        self.versions["versions"].append(tmp)

