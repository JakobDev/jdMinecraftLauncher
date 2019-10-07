#!/usr/bin/env python3
import subprocess
import os

def runMinecraft(profile,env):
    versiontype, versionid = profile.getVersion().split(" ")
    currentDir = os.path.dirname(os.path.realpath(__file__))
    result = subprocess.run(["java","-jar",os.path.join(currentDir,"mclauncher-cmd.jar"),"command",versionid,env.dataPath], stdout=subprocess.PIPE)
    command = result.stdout.decode().replace("\n","")[4:]
    if profile.customArguments:
        command = command.replace("-Xms512M -Xmx512M",profile.arguments)
    command = command.replace("{username}",env.account["name"])
    command = command.replace("{uuid}",env.account["uuid"])
    command = command.replace("{accesToken}",env.account["accessToken"])
    #In a few Versions the APi adds this automatic
    if command.find("--width ${resolution_width} --height ${resolution_height}") == -1:
        command = command + "--width ${resolution_width} --height ${resolution_height}"
    if profile.customResolution:
        command = command.replace("${resolution_width}",profile.resolutionX)
        command = command.replace("${resolution_height}",profile.resolutionY)
    else:
        command = command.replace("--width ${resolution_width} --height ${resolution_height}","")
    command = command.replace("${version_type}",versiontype)
    command = command.replace("-gameDir " + env.dataPath,"-gameDir {gameDir}")
    words = command.split()
    commandlist = []
    for w in words:
        if w == "{gameDir}":
            commandlist.append(profile.getGameDirectoryPath())
        else:
            commandlist.append(w)
    if profile.serverConnect:
        commandlist.append("--server")
        commandlist.append(profile.serverIP)
        if profile.serverPort != "":
            commandlist.append("--port")
            commandlist.append(profile.serverPort)
    return commandlist
    
    
