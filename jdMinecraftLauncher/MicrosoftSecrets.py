from .Globals import Globals
from typing import Optional
import json
import os


class MicrosoftSecrets:
    _instance: Optional["MicrosoftSecrets"] = None

    @classmethod
    def getInstance(cls) -> "MicrosoftSecrets":
        if cls._instance is None:
            cls._instance = cls()

        return cls._instance

    def __init__(self) -> None:
        # In my opinion, it is not possible to hide the credentials from a person who really want it
        # This little "encryption" ist just to hide it from Bots

        self.clientID = ""
        self.secret = ""
        self.redirectURL = ""

        if os.path.isfile(os.path.join(Globals.dataDir, "secrets.json")):
            with open(os.path.join(Globals.dataDir, "secrets.json"), "r", encoding="utf-8") as f:
                self._jsonData = json.load(f)
        elif os.path.isfile(os.path.join(Globals.programDir, "secrets.json")):
            with open(os.path.join(Globals.programDir, "secrets.json"), "r", encoding="utf-8") as f:
                self._jsonData = json.load(f)

        self._decrypt("clientID", "clientID")
        self._decrypt("secret", "secret")
        self._decrypt("redirectURL", "redirectURL")

    def _decrypt(self, json_key: str, obj_key: str) -> None:
        if self._jsonData[json_key] is None:
            setattr(self, obj_key, None)
            return

        if not self._jsonData["encrypted"]:
            setattr(self, obj_key, self._jsonData[json_key])
            return

        text = self._jsonData[json_key][::-1]
        result = ""

        for c in text:
            result += chr(ord(c) - 5)

        setattr(self, obj_key, result)
