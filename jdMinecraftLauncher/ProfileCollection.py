from jdMinecraftLauncher.Profile import Profile
from typing import Optional, TYPE_CHECKING
import json
import os


if TYPE_CHECKING:
    from jdMinecraftLauncher.Environment import Environment


class ProfileCollection:
    def __init__(self, env: "Environment"):
        self.profileList: list[Profile] = []
        self.selectedProfile = ""
        self._env = env

    def loadProfiles(self) -> None:
        profileJSON = os.path.join(self._env.dataDir, "profiles.json")

        if not os.path.isfile(profileJSON):
            defaultProfile = Profile("Default", self._env)
            self.selectedProfile = defaultProfile.id
            self.profileList.append(defaultProfile)
            return

        with open(profileJSON, "r", encoding="utf-8") as f:
            data = json.load(f)

        profileVersion = data.get("version", 0)

        self.selectedProfile = data.get("selectedProfile", "")

        for i in data["profileList"]:
            self.profileList.append(Profile.load(self._env, i, profileVersion))

        if profileVersion != 1:
            self.save()

    def save(self) -> None:
        if self._env.args.dont_save_data:
            return

        data = {"selectedProfile": self.selectedProfile, "profileList": []}
        for i in self.profileList:
            data["profileList"].append(i.toDict())
        data["version"] = 1

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
        return self.getProfileByID(self.selectedProfile)
