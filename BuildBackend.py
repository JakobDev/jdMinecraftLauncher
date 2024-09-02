# This file is used durring the build process
from setuptools import build_meta as origin
from typing import Optional, Any
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


def compile_ui(path: str) -> None:
    if shutil.which("pyuic6") is None:
        print("pyuic6 was not found", file=sys.stderr)
        sys.exit(1)

    program_dir = pathlib.Path(path) / "jdMinecraftLauncher"
    compiled_dir = program_dir / "ui_compiled"
    source_dir = program_dir / "ui"

    try:
        shutil.rmtree(compiled_dir)
    except FileNotFoundError:
        pass

    compiled_dir.mkdir()
    (compiled_dir / "__init__.py").touch()

    for i in source_dir.iterdir():
        if i.suffix != ".ui":
            continue

        subprocess.run(["pyuic6", str(i), "-o", str(compiled_dir / f"{i.stem}.py")], check=True)


def build_translations(path: str) -> None:
    command = get_lrelease_command()
    for i in TRANSLATION_DIRS:
        for ts in pathlib.Path(os.path.join(path, i)).iterdir():
            subprocess.run([command, str(ts), "-qm", os.path.join(path, i, ts.stem + ".qm")], check=True)
            os.remove(ts)


prepare_metadata_for_build_wheel = origin.prepare_metadata_for_build_wheel
get_requires_for_build_sdist = origin.get_requires_for_build_sdist
build_sdist = origin.build_sdist


def build_wheel(wheel_directory: str, config_settings: Any = None, metadata_directory: Optional[str] = None) -> str:
    if get_lrelease_command() is None:
        print("lrealease was not found", file=sys.stderr)
        sys.exit(1)

    wheel_name = origin.build_wheel(wheel_directory, config_settings=config_settings, metadata_directory=metadata_directory)
    wheel_path = os.path.join(wheel_directory, wheel_name)
    with tempfile.TemporaryDirectory() as tempdir:
        subprocess.run(["wheel", "unpack", "--dest", tempdir, wheel_path])
        current_dir = os.path.join(tempdir, os.listdir(tempdir)[0])

        compile_ui(current_dir)
        build_translations(current_dir)

        try:
            os.remove(os.path.join(current_dir, os.path.basename(__file__)))
        except FileNotFoundError:
            pass

        try:
            shutil.rmtree(os.path.join(current_dir, "jdMinecraftLauncher", "ui"))
        except FileNotFoundError:
            pass

        subprocess.run(["wheel", "pack", "--dest-dir", wheel_directory, current_dir])

    return wheel_name


def get_requires_for_build_wheel(self: Any, config_settings: Any = None) -> list[str]:
    if get_lrelease_command() is None:
        return origin.get_requires_for_build_wheel() + ["PySide6"]
    else:
        return origin.get_requires_for_build_wheel()
