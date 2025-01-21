from .Functions import isFlatpak, isWayland
from .Constants import DisplayServerSetting
from typing import List, TYPE_CHECKING
import minecraft_launcher_lib
import pathlib
import shutil
import shlex
import os


if TYPE_CHECKING:
    from .Environment import Environment
    from .Profile import Profile


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
        command += ["--sandbox-expose-path=" + str(pathlib.Path(profile.executable).parent.parent)]

    return command


def getMinecraftCommand(profile: "Profile", env: "Environment", natives_path: str) -> List[str]:
    version = profile.getVersionID()

    account = env.accountManager.getSelectedAccount()

    options: minecraft_launcher_lib.types.MinecraftOptions = {
        "username": account.getName(),
        "uuid": account.getMinecraftUUID(),
        "token": account.getAccessToken(),
        "launcherName": "jdMinecraftLauncher",
        "launcherVersion": env.launcherVersion,
        "gameDirectory": profile.getGameDirectoryPath(),
    }

    if profile.customExecutable:
        options["executablePath"] = profile.executable

    if profile.customArguments:
        options["jvmArguments"] = shlex.split(profile.arguments)

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
        command += shlex.split(profile.minecraftOptions)

    if profile.useGameMode and shutil.which("gamemoderun"):
        command.insert(0, "gamemoderun")

    if isFlatpak() and env.settings.get("useFlatpakSubsandbox"):
        command = _getFlatpakSpawnCommand(profile, env) + command

    if isWayland():
        match env.settings.get("displayServer"):
            case DisplayServerSetting.WAYLAND:
                command = ["env", "-u", "DISPLAY"] + command
            case DisplayServerSetting.XWAYLAND:
                command = ["env", "-u", "WAYLAND_DISPLAY"] + command

    return command
