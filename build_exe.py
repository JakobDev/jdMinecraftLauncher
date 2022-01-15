#!/usr/bin/env python3
from cx_Freeze import setup, Executable
import platform

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
    version = "3.0",
    description = "A Minecraft Launcher writen in Python",
    options = {"build_exe": build_exe_options},
    executables = [target]
)
