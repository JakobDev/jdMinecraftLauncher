from typing import Optional, TYPE_CHECKING
import json
import os


if TYPE_CHECKING:
    from jdMinecraftLauncher.Environment import Environment


class MicrosoftSecrets:
    _instance: Optional["MicrosoftSecrets"] = None

    def __init__(self, env: "Environment") -> None:
        # In my opinion, it is not possible to hide the credentials from a person who really want it
        # This little "encryption" ist just to hide it from Bots

        self.client_id = ""
        self.secret = ""
        self.redirect_url = ""

        if os.path.isfile(os.path.join(env.dataDir, "secrets.json")):
            with open(os.path.join(env.dataDir, "secrets.json"), "r", encoding="utf-8") as f:
                self._json_data = json.load(f)
        elif os.path.isfile(os.path.join(env.currentDir, "secrets.json")):
            with open(os.path.join(env.currentDir, "secrets.json"), "r", encoding="utf-8") as f:
                self._json_data = json.load(f)
        else:
            pass

        self._decrypt("clientID", "client_id")
        self._decrypt("secret", "secret")
        self._decrypt("redirectURL", "redirect_url")

    def _decrypt(self, json_key: str, obj_key: str) -> None:
        if self._json_data[json_key] is None:
            setattr(self, obj_key, None)
            return
        if not self._json_data["encrypted"]:
            setattr(self, obj_key, self._json_data[json_key])
            return
        text = self._json_data[json_key][::-1]
        result = ""
        for c in text:
            result += chr(ord(c) - 5)
        setattr(self, obj_key, result)

    @classmethod
    def setup(cls, env: "Environment") -> None:
        cls._instance = cls(env)

    @classmethod
    def get_secrets(cls) -> "MicrosoftSecrets":
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance
