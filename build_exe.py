#!/usr/bin/env python3
from cx_Freeze import setup, Executable
import platform
import os


with open(os.path.join(os.path.dirname(__file__), "jdMinecraftLauncher", "version.txt"), "r", encoding="utf-8") as f:
    version = f.read().strip()

if platform.system() == "Windows":
    build_exe_options = {"excludes": ["tkinter"]}
    target = Executable(
        script="jdMinecraftLauncher.py",
        base="Win32GUI",
        target_name = "jdMinecraftLauncher.exe",
        icon="deploy/Icon.ico"
    )
else:
    build_exe_options = {"excludes": ["tkinter", "test"]}
    target = Executable(script="jdMinecraftLauncher.py",)

setup(
    name = "jdMinecraftLauncher",
    version = version,
    description = "A Minecraft Launcher writen in Python",
    options = {"build_exe": build_exe_options},
    executables = [target]
)
