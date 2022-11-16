from typing import TYPE_CHECKING
import json
import os


if TYPE_CHECKING:
    from jdMinecraftLauncher.Environment import Environment


class Settings:
    def __init__(self, env: "Environment"):
        self.language = "default"
        self.newsURL = "https://www.minecraft.net"
        self.enableMultiLaunch = False
        self.extractNatives = False

        if os.path.isfile(os.path.join(env.dataDir, "settings.json")):
            self.load(os.path.join(env.dataDir, "settings.json"))

    def load(self, path: str):
        try:
            with open(path,"r",encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            print("The settings can't be loaded. jdMinecraftLauncher will use the default settings.")
            return
        settings = vars(self)
        for key, value in data.items():
            settings[key] = value
        
    def save(self, path: str):
        data = vars(self)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

