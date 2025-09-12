from PyQt6.QtCore import QObject, QCoreApplication, pyqtSignal
from jdMinecraftLauncher.Profile import Profile
from typing import cast, Optional
from ..Globals import Globals
import traceback
import copy
import json
import uuid
import sys
import os


class ProfileCollection(QObject):
    _instance: Optional["ProfileCollection"] = None

    profilesChanged = pyqtSignal()

    @classmethod
    def getInstance(cls) -> "ProfileCollection":
        if cls._instance is None:
            cls._instance = cls()

        return cls._instance

    def __init__(self) -> None:
        super().__init__()

        self._profileList: list[Profile] = []
        self._loadError: str | None = None
        self._selectedProfile = ""

        self.loadProfiles()

    def _generateProfileID(self) -> str:
        while True:
            currentID = str(uuid.uuid4())
            for profile in self._profileList:
                if profile.id == currentID:
                    break
            else:
                return currentID

    def loadProfiles(self) -> None:
        profileJSON = os.path.join(Globals.dataDir, "profiles.json")

        if not os.path.isfile(profileJSON):
            defaultProfile = Profile(self._generateProfileID(), QCoreApplication.translate("ProfileCollection", "Default"))
            self._selectedProfile = defaultProfile.id
            self._profileList.append(defaultProfile)
            return

        try:
            with open(profileJSON, "r", encoding="utf-8") as f:
                data = json.load(f)

            profileVersion = data.get("version", 0)

            self._selectedProfile = data.get("selectedProfile", "")

            for i in data["profileList"]:
                self._profileList.append(Profile.load(i, profileVersion))

            if profileVersion != 1:
                self.save()
        except Exception:
            self._loadError = traceback.format_exc()
            print(self._loadError, file=sys.stderr)

            if len(self._profileList) == 0:
                defaultProfile = Profile(self._generateProfileID(), "Default")
                self._selectedProfile = defaultProfile.id
                self._profileList.append(defaultProfile)
                return

        self.profilesChanged.emit()

    def save(self) -> None:
        if Globals.dontSaveData:
            return

        data = {"selectedProfile": self._selectedProfile, "profileList": []}
        for i in self._profileList:
            cast(list[dict], data["profileList"]).append(i.toDict())
        data["version"] = 1  # type: ignore

        with open(os.path.join(Globals.dataDir, "profiles.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def createProfile(self, name: str) -> Profile:
        return Profile(self._generateProfileID(), name)

    def getProfileList(self) -> list[Profile]:
        returnList: list[Profile] = []

        for profile in self._profileList:
            returnList.append(copy.deepcopy(profile))

        return returnList

    def updateProfile(self, profile: Profile) -> None:
        profile = copy.deepcopy(profile)

        for pos, currentProfile in enumerate(self._profileList):
            if currentProfile.id == profile.id:
                self._profileList[pos] = profile
                self.profilesChanged.emit()
                return

        self._profileList.append(profile)
        self.profilesChanged.emit()

    def getProfileByName(self, name: str) -> Optional[Profile]:
        for profile in self._profileList:
            if profile.name == name:
                return copy.deepcopy(profile)

        return None

    def getProfileByID(self, profile_id: str) -> Optional[Profile]:
        for profile in self._profileList:
            if profile.id == profile_id:
                return copy.deepcopy(profile)

        return None

    def getSelectedProfile(self) -> Profile:
        profile = self.getProfileByID(self._selectedProfile)

        if profile is not None:
            return profile
        else:
            return copy.deepcopy(self._profileList[0])

    def setSelectedProfile(self, profile: Profile) -> None:
        self._selectedProfile = profile.id

    def getLoadError(self) -> Optional[str]:
        return self._loadError

    def removeProfileById(self, profileId: str) -> None:
        for pos, profile in enumerate(self._profileList):
            if profile.id == profileId:
                del self._profileList[pos]
                break

        if self._selectedProfile == profileId:
            self._selectedProfile = self._profileList[0].id

        self.profilesChanged.emit()
