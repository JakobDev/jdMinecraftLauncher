from typing import List, TYPE_CHECKING
from .Functions import isFlatpak
import minecraft_launcher_lib
import pathlib
import shutil
import os


if TYPE_CHECKING:
    from jdMinecraftLauncher.Environment import Environment
    from jdMinecraftLauncher.Profile import Profile


def _getFlatpakSpawnCommand(profile: "Profile", env: "Environment") -> List[str]:
    command = [
                "flatpak-spawn",
                "--sandbox",
                "--sandbox-flag=share-display",
                "--sandbox-flag=share-sound",
                "--sandbox-flag=share-gpu",
                "--sandbox-flag=allow-dbus",
                "--sandbox-flag=allow-a11y"
            ]

    if profile.customGameDirectory:
        command += [
            f"--sandbox-expose-path-ro={env.minecraftDir}",
            f"--sandbox-expose-path={profile.getGameDirectoryPath()}",
            "--sandbox-expose-path=" + os.path.join(env.minecraftDir, "versions", profile.getVersionID()),
        ]
    else:
        command += [f"--sandbox-expose-path={env.minecraftDir}"]

    if profile.customExecutable:
        command += ["--sandbox-expose-path=" + pathlib.Path(profile.executable).parent.parent]

    return command


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

    if isFlatpak() and env.settings.get("useFlatpakSubsandbox"):
        command = _getFlatpakSpawnCommand(profile, env) + command

    return _getFlatpakSpawnCommand(profile, env) + command
