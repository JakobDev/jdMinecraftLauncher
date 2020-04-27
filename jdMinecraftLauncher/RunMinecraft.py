import minecraft_launcher_lib
import subprocess

def runMinecraft(profile,env):
    versiontype, versionid = profile.getVersion().split(" ")
    options = {
        "username": env.account["name"],
        "uuid": env.account["uuid"],
        "token": env.account["accessToken"],
        "launcherName": "jdMinecraftLauncher",
        "launcherVersion": env.launcherVersion,
        "gameDirectory": profile.getGameDirectoryPath(),
    }
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
    command = minecraft_launcher_lib.command.get_minecraft_command(versionid,env.dataPath,options)
    command = command[1:]
    return command
