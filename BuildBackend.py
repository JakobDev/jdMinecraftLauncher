# This file is used durring the build process
from setuptools import build_meta as origin
from typing import Optional
import subprocess
import tempfile
import pathlib
import shutil
import sys
import os


TRANSLATION_DIRS = [
    "jdMinecraftLauncher/translations"
]


def get_lrelease_command() -> Optional[str]:
    for i in ("lrelease", "lrelease6", "pyside6-lrelease", "pyside5-lrelease"):
        if shutil.which(i) is not None:
            return i
    return None


def build_translations(path: str) -> None:
    command = get_lrelease_command()
    for i in TRANSLATION_DIRS:
        for ts in pathlib.Path(os.path.join(path, i)).iterdir():
            subprocess.run([command, str(ts), "-qm", os.path.join(path, i, ts.stem + ".qm")], check=True)
            os.remove(ts)


prepare_metadata_for_build_wheel = origin.prepare_metadata_for_build_wheel
get_requires_for_build_sdist = origin.get_requires_for_build_sdist
build_sdist = origin.build_sdist


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    if get_lrelease_command() is None:
        print("lrealease was not found", file=sys.stderr)
        sys.exit(1)

    wheel_name =  origin.build_wheel(wheel_directory, config_settings=config_settings, metadata_directory=metadata_directory)
    wheel_path = os.path.join(wheel_directory, wheel_name)
    with tempfile.TemporaryDirectory() as tempdir:
        subprocess.run(["wheel", "unpack", "--dest", tempdir, wheel_path])
        current_dir = os.path.join(tempdir, os.listdir(tempdir)[0])

        build_translations(current_dir)

        try:
            os.remove(os.path.join(current_dir, os.path.basename(__file__)))
        except FileNotFoundError:
            pass

        subprocess.run(["wheel", "pack", "--dest-dir", wheel_directory, current_dir])
    return wheel_name


def get_requires_for_build_wheel(self, config_settings=None) -> list[str]:
    if get_lrelease_command() is None:
        return origin.get_requires_for_build_wheel() + ["PySide6"]
    else:
        return origin.get_requires_for_build_wheel()
