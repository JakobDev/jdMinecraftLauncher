#!/usr/bin/env python3
import subprocess
import shutil
import pysftp
import os

rootDir = os.path.dirname(os.path.realpath(__file__))[:-7]
version = os.getenv("CI_COMMIT_TAG")

os.mkdir(os.path.join(rootDir,"work"))
os.mkdir(os.path.join(rootDir,"output"))

workdir = os.path.join(rootDir,"work")

shutil.copytree(os.path.join(rootDir,"jdMinecraftLauncher"),os.path.join(workdir,"jdMinecraftLauncher"))
shutil.copyfile(os.path.join(rootDir,"jdMinecraftLauncher.py"),os.path.join(workdir,"jdMinecraftLauncher.py"))
shutil.copyfile(os.path.join(rootDir,"README.md"),os.path.join(workdir,"README.md"))
shutil.copyfile(os.path.join(rootDir,"LICENSE"),os.path.join(workdir,"LICENCE"))
shutil.copyfile(os.path.join(rootDir,"requirements.txt"),os.path.join(workdir,"requirements.txt"))

zipOutput = os.path.join(rootDir,"output","jdMinecraftLauncher-" + version + "-Python")
shutil.make_archive(zipOutput,'zip',workdir)

zipOutput = zipOutput + ".zip"

#Create windows zip
exe_dir_name = os.listdir(os.path.join(rootDir,"build"))[0]
exe_dir_path = os.path.join(rootDir,"build",exe_dir_name)

windowsOutput = os.path.join(rootDir,"output","jdMinecraftLauncher-" + version + "-Windows")
shutil.make_archive(windowsOutput,'zip',exe_dir_path)

windowsOutput = windowsOutput + ".zip"

#Upload files
cnopts = pysftp.CnOpts()
cnopts.hostkeys = None
server = pysftp.Connection(host="frs.sourceforge.net",username=os.getenv("SOURCEFORGE_USERNAME"),password=os.getenv("SOURCEFORGE_PASSWORD"),cnopts=cnopts)
server.chdir("/home/frs/project/jdminecraftlauncher")
server.mkdir(version)
server.chdir("/home/frs/project/jdminecraftlauncher/" + version)
server.put(zipOutput)
server.put(windowsOutput)
server.close()

subprocess.call(["curl","-H","Accept: application/json","-X","PUT","-d","default=mac&default=linux&default=bsd&default=solaris&default=others","-d","api_key=" + os.getenv("SOURCEFORGE_API_KEY"),"https://sourceforge.net/projects/jdminecraftlauncher/files/" + version + "/jdMinecraftLauncher-" + version + "-Python.zip"])
subprocess.call(["curl","-H","Accept: application/json","-X","PUT","-d","default=windows","-d","api_key=" + os.getenv("SOURCEFORGE_API_KEY"),"https://sourceforge.net/projects/jdminecraftlauncher/files/" + version + "/jdMinecraftLauncher-" + version + "-Windows.zip"])
