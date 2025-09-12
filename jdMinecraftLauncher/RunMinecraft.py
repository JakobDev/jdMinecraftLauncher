from .core.AccountManager import AccountManager
from PyQt6.QtCore import QProcessEnvironment
from .Functions import isFlatpak, isWayland
from .Constants import DisplayServerSetting
from typing import TypedDict, TYPE_CHECKING
from .Settings import Settings
import minecraft_launcher_lib
from .Globals import Globals
import pathlib
import shutil
import shlex
import os


if TYPE_CHECKING:
    from .Profile import Profile


class CommandResult(TypedDict):
    command: list[str]
    env: QProcessEnvironment


def _getFlatpakSpawnCommand(profile: "Profile") -> list[str]:
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
            f"--sandbox-expose-path-ro={Globals.minecraftDir}",
            f"--sandbox-expose-path={profile.getGameDirectoryPath()}",
            "--sandbox-expose-path=" + os.path.join(Globals.minecraftDir, "versions", profile.getVersionID()),
        ]
    else:
        command += [f"--sandbox-expose-path={Globals.minecraftDir}"]

    if profile.customExecutable:
        command += ["--sandbox-expose-path=" + str(pathlib.Path(profile.executable).parent.parent)]

    return command


def getMinecraftCommand(profile: "Profile", natives_path: str | None) -> CommandResult:
    version = profile.getVersionID()

    account = AccountManager.getInstance().getSelectedAccount()

    options: minecraft_launcher_lib.types.MinecraftOptions = {
        "username": account.getName(),
        "uuid": account.getMinecraftUUID(),
        "token": account.getAccessToken(),
        "launcherName": "jdMinecraftLauncher",
        "launcherVersion": Globals.launcherVersion,
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

    if natives_path is not None:
        options["nativesDirectory"] = natives_path
        minecraft_launcher_lib.natives.extract_natives(version, Globals.minecraftDir, natives_path)

    command = minecraft_launcher_lib.command.get_minecraft_command(version, Globals.minecraftDir, options)

    if profile.hasMinecraftOptions:
        command += shlex.split(profile.minecraftOptions)

    if profile.useGameMode and shutil.which("gamemoderun"):
        command.insert(0, "gamemoderun")

    settings = Settings.getInstance()

    if isFlatpak() and settings.get("useFlatpakSubsandbox"):
        command = _getFlatpakSpawnCommand(profile) + command

    env = QProcessEnvironment.systemEnvironment()

    if isWayland():
        match settings.get("displayServer"):
            case DisplayServerSetting.WAYLAND:
                env.insert("XDG_SESSION_TYPE", "wayland")
                env.remove("DISPLAY")
            case DisplayServerSetting.XWAYLAND:
                env.insert("XDG_SESSION_TYPE", "x11")
                env.remove("WAYLAND_DISPLAY")

    return {
        "command": command,
        "env": env,
    }
