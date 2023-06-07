#!/usr/bin/env python
import subprocess
import pathlib


def main() -> None:
    root_path = pathlib.Path(__file__).parent.parent
    pot_path = str(root_path / "deploy" / "translations" / "messages.pot")

    subprocess.run(["xgettext", "-l", "xml", "--its", str(root_path / "deploy" / "translations" / "AppStream.its"), "-o", pot_path, "deploy/page.codeberg.JakobDev.jdMinecraftLauncher.metainfo.xml"], cwd=root_path, check=True)
    subprocess.run(["xgettext", "-l", "desktop", "-k", "-kComment", "-o", pot_path, "-j", "deploy/page.codeberg.JakobDev.jdMinecraftLauncher.desktop"], cwd=root_path, check=True)

    for file in (root_path / "deploy" / "translations").iterdir():
        if file.suffix == ".po":
            subprocess.run(["msgmerge", "-o", str(file), str(file), pot_path], check=True)


if __name__ == "__main__":
    main()
