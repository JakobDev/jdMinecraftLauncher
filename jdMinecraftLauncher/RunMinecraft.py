from typing import List, TYPE_CHECKING
import minecraft_launcher_lib
import shutil


if TYPE_CHECKING:
    from jdMinecraftLauncher.Environment import Environment
    from jdMinecraftLauncher.Profile import Profile


def getMinecraftCommand(profile: "Profile", env: "Environment", natives_path: str) -> List[str]:
    version = profile.getVersionID()
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

    if profile.disableMultiplayer:
        options["disableMultiplayer"] = True

    if profile.disableChat:
        options["disableChat"] = True

    if natives_path != "":
        options["nativesDirectory"] = natives_path
        minecraft_launcher_lib.natives.extract_natives(version, env.minecraftDir, natives_path)

    command = minecraft_launcher_lib.command.get_minecraft_command(version, env.minecraftDir, options)

    if profile.hasMinecraftOptions:
        command += profile.minecraftOptions.strip().split(" ")

    if profile.useGameMode and shutil.which("gamemoderun"):
        command.insert(0, "gamemoderun")

    return command
