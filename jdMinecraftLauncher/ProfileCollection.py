from typing import cast, Optional, TYPE_CHECKING
from jdMinecraftLauncher.Profile import Profile
from PyQt6.QtCore import QCoreApplication
import traceback
import json
import sys
import os


if TYPE_CHECKING:
    from jdMinecraftLauncher.Environment import Environment


class ProfileCollection:
    def __init__(self, env: "Environment") -> None:
        self.profileList: list[Profile] = []
        self._loadError: str | None = None
        self.selectedProfile = ""
        self._env = env

    def loadProfiles(self) -> None:
        profileJSON = os.path.join(self._env.dataDir, "profiles.json")

        if not os.path.isfile(profileJSON):
            defaultProfile = Profile(QCoreApplication.translate("ProfileCollection", "Default"), self._env)
            self.selectedProfile = defaultProfile.id
            self.profileList.append(defaultProfile)
            return

        try:
            with open(profileJSON, "r", encoding="utf-8") as f:
                data = json.load(f)

            profileVersion = data.get("version", 0)

            self.selectedProfile = data.get("selectedProfile", "")

            for i in data["profileList"]:
                self.profileList.append(Profile.load(self._env, i, profileVersion))

            if profileVersion != 1:
                self.save()
        except Exception:
            self._loadError = traceback.format_exc()
            print(self._loadError, file=sys.stderr)

            if len(self.profileList) == 0:
                defaultProfile = Profile("Default", self._env)
                self.selectedProfile = defaultProfile.id
                self.profileList.append(defaultProfile)
                return

    def save(self) -> None:
        if self._env.args.dont_save_data:
            return

        data = {"selectedProfile": self.selectedProfile, "profileList": []}
        for i in self.profileList:
            cast(list[dict], data["profileList"]).append(i.toDict())
        data["version"] = 1  # type: ignore

        with open(os.path.join(self._env.dataDir, "profiles.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def getProfileByName(self, name: str) -> Optional[Profile]:
        for i in self.profileList:
            if i.name == name:
                return i
        return None

    def getProfileByID(self, profile_id: str) -> Optional[Profile]:
        for i in self.profileList:
            if i.id == profile_id:
                return i
        return None

    def getSelectedProfile(self) -> Profile:
        profile = self.getProfileByID(self.selectedProfile)
        if profile is not None:
            return profile
        else:
            return self.profileList[0]

    def getLoadError(self) -> Optional[str]:
        return self._loadError

    def removeProfileById(self, profileId: str) -> None:
        for pos, profile in enumerate(self.profileList):
            if profile.id == profileId:
                del self.profileList[pos]
                break

        if self.selectedProfile == profileId:
            self.selectedProfile = self.profileList[0].id
