import minecraft_launcher_lib
from typing import List
import shutil


def getMinecraftCommand(profile, env, natives_path) -> List[str]:
    versiontype, versionid = profile.getVersion().split(" ")
    options = {
        "username": env.account["name"],
        "uuid": env.account["uuid"],
        "token": env.account["accessToken"],
        "launcherName": "jdMinecraftLauncher",
        "launcherVersion": env.launcherVersion,
        "gameDirectory": profile.getGameDirectoryPath(),
    }
    if profile.customExecutable:
        options["executablePath"] = profile.executable
    if profile.customArguments:
        options["jvmArguments"] = []
        for i in profile.arguments.split(" "):
            options["jvmArguments"].append(i)
    if profile.customResolution:
        options["customResolution"] = True
        options["resolutionWidth"] = profile.resolutionX
        options["resolutionHeight"] = profile.resolutionY
    if profile.serverConnect:
        options["server"] = profile.serverIP
        if profile.serverPort != "":
            options["port"] = profile.serverPort
    if profile.demoMode:
        options["demo"] = True
    if natives_path != "":
        options["nativesDirectory"] = natives_path
        minecraft_launcher_lib.natives.extract_natives(versionid,env.minecraftDir, natives_path)
    command = minecraft_launcher_lib.command.get_minecraft_command(versionid, env.minecraftDir, options)
    if profile.useGameMode and shutil.which("gamemoderun"):
        command.insert(0, "gamemoderun")
    return command
