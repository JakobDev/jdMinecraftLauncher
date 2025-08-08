#!/usr/bin/env python
from typing import Optional
import subprocess
import pathlib
import shutil
import sys
import os


def get_lrelease_from_qmake() -> Optional[str]:
    try:
        result = subprocess.run(["qmake6", "-query", "QT_HOST_BINS"], capture_output=True, check=True)
    except Exception:
        return None

    path = os.path.join(result.stdout.decode("utf-8").strip(), "lrelease")

    if os.path.isfile(path):
        return path
    else:
        return None


def get_lrelease_command() -> Optional[str]:
    if (lrelease_path := get_lrelease_from_qmake()) is not None:
        return lrelease_path

    for i in ("lrelease", "pyside6-lrelease", "pyside5-lrelease"):
        if shutil.which(i) is not None:
            return i
    return None


def main() -> None:
    command = get_lrelease_command()

    if command is None:
        print("lrelease not found", file=sys.stderr)
        sys.exit(1)

    translation_dir = (pathlib.Path(__file__).parent.parent / "jdMinecraftLauncher" / "translations")
    for i in translation_dir.iterdir():
        if i.suffix == ".ts":
            subprocess.run([command, str(i), "-qm", os.path.join(translation_dir, i.stem + ".qm")])


if __name__ == "__main__":
    main()
