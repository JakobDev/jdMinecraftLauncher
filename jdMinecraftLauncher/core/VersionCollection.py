from typing import TypedDict, Literal, Optional
from PyQt6.QtCore import QObject, pyqtSignal
from ..Globals import Globals
import requests
import shutil
import json
import os


class VersionData(TypedDict):
    id: str
    type: Literal["release", "snapshot", "old_beta", "old_alpha"]


class VersionCollection(QObject):
    _instance: Optional["VersionCollection"] = None

    versionsUpdated = pyqtSignal()

    @classmethod
    def getInstance(cls) -> "VersionCollection":
        if cls._instance is None:
            cls._instance = cls()

        return cls._instance

    def __init__(self) -> None:
        super().__init__()

        self._installedVersions: dict[str, VersionData] = {}
        self._vanillaVersions: dict[str, VersionData] = {}
        self._versions: dict[str, VersionData] = {}
        self._latestSnapshot = ""
        self._latestRelease = ""

        self._loadVanillaVersions()
        self.updateVersions()

    def _loadVanillaVersions(self) -> None:
        if Globals.offlineMode:
            with open(os.path.join(Globals.dataDir, "versions_cache.json"), "r", encoding="utf-8") as f:
                versionData = json.load(f)
        else:
            versionData = requests.get("https://launchermeta.mojang.com/mc/game/version_manifest_v2.json").json()

            with open(os.path.join(Globals.dataDir, "versions_cache.json"), "w", encoding="utf-8") as f:
                json.dump(versionData, f, ensure_ascii=False, indent=4)

        self._latestRelease = versionData["latest"]["release"]
        self._latestSnapshot = versionData["latest"]["snapshot"]

        for currentVersion in versionData["versions"]:
            self._vanillaVersions[currentVersion["id"]] = {
                "id": currentVersion["id"],
                "type": currentVersion["type"],
            }

    def updateVersions(self) -> None:
        installedVersions: dict[str, VersionData] = {}
        versionDict: dict[str, VersionData] = {}

        for key, value in self._vanillaVersions.items():
            versionDict[key] = value

        if not os.path.isdir(os.path.join(Globals.minecraftDir, "versions")):
            self._versions = versionDict
            return

        for currentVersion in os.listdir(os.path.join(Globals.minecraftDir, "versions")):
            jsonPath = os.path.join(Globals.minecraftDir, "versions", currentVersion, f"{currentVersion}.json")

            if not os.path.isfile(jsonPath):
                continue

            with open(jsonPath, "r", encoding="utf-8") as f:
                try:
                    versionInfo = json.load(f)
                except json.decoder.JSONDecodeError as e:
                    print(f"Error while parsing {jsonPath}: {e.args[0]}")
                    continue

            installedVersions[versionInfo["id"]] = {
                "id": versionInfo["id"],
                "type": versionInfo["type"],
            }

        for key, value in installedVersions.items():
            versionDict[key] = value

        self._installedVersions = installedVersions
        self._versions = versionDict

        self.versionsUpdated.emit()

    def getVersionList(self) -> list[VersionData]:
        return list(self._versions.values())

    def getInstalledVersions(self) -> list[VersionData]:
        return list(self._installedVersions.values())

    def getLatestRelease(self) -> str:
        return self._latestRelease

    def getLatestSnapshot(self) -> str:
        return self._latestSnapshot

    def uninstallVersion(self, version: str) -> None:
        shutil.rmtree(os.path.join(Globals.minecraftDir, "versions", version))
        self.updateVersions()
