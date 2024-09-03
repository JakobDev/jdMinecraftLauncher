#!/usr/bin/env python
import xml.etree.ElementTree
import subprocess
import argparse
import shutil
import sys
import os


def install_data_file(src: str, dest: str) -> None:
    try:
        os.makedirs(os.path.dirname(dest))
    except FileExistsError:
        pass
    except PermissionError as ex:
        print(f"Don't have Permission to create {ex.filename}. Use --prefix to change the Prefix.", file=sys.stderr)
        sys.exit(1)

    try:
        shutil.copyfile(src, dest)
        os.chmod(dest, 0o644)
    except PermissionError as ex:
        print(f"Don't have Permission to create {ex.filename}. Use --prefix to change the Prefix.", file=sys.stderr)
        sys.exit(1)


def create_directory(path: str) -> None:
    try:
        os.makedirs(path)
    except FileExistsError:
        pass
    except PermissionError as ex:
        print(f"Don't have Permission to create {ex.filename}. Use --prefix to change the Prefix.", file=sys.stderr)


def get_translation_percentage(path: str) -> int:
    root = xml.etree.ElementTree.parse(path).getroot()
    all_messages = len(root.findall("context/message/translation"))
    untranslated_messages = len(root.findall("context/message/translation[@type='unfinished']"))
    translated_messages = (all_messages - untranslated_messages)
    return int((translated_messages / all_messages) * 100)


def write_translation_status(project_root: str, appstream_path: str) -> None:
    languages_tag = xml.etree.ElementTree.Element("languages")

    en_tag = xml.etree.ElementTree.Element("lang")
    en_tag.set("percentage", "100")
    en_tag.text = "en"
    languages_tag.append(en_tag)

    translation_dir = os.path.join(project_root, "jdMinecraftLauncher", "translations")
    for translation_file in os.listdir(translation_dir):
        if not translation_file.endswith(".ts"):
            continue

        language = translation_file.removeprefix("jdMinecraftLauncher_").removesuffix(".ts")
        lang_tag = xml.etree.ElementTree.Element("lang")
        lang_tag.set("percentage", str(get_translation_percentage(os.path.join(translation_dir, translation_file))))
        lang_tag.text = language
        languages_tag.append(lang_tag)

    appstream_tree = xml.etree.ElementTree.parse(appstream_path)
    appstream_root = appstream_tree.getroot()
    appstream_root.append(languages_tag)
    appstream_tree.write(appstream_path, encoding="unicode", xml_declaration=True)


def main() -> None:
    if not shutil.which("msgfmt"):
        print("msgfmt not found. You need to install gettext for the installation.")
        sys.exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument("--prefix", default="/usr", help="The Prefix to install the files")
    args = parser.parse_args()

    project_root = os.path.dirname(__file__)

    install_data_file(os.path.join(project_root, "jdMinecraftLauncher", "Icon.svg"), os.path.join(args.prefix, "share", "icons", "hicolor", "scalable", "apps", "page.codeberg.JakobDev.jdMinecraftLauncher.svg"))
    install_data_file(os.path.join(project_root, "deploy", "page.codeberg.JakobDev.jdMinecraftLauncher.service"), os.path.join(args.prefix, "share", "dbus-1", "services", "page.codeberg.JakobDev.jdMinecraftLauncher.service"))

    create_directory(os.path.join(args.prefix, "share", "applications"))
    create_directory(os.path.join(args.prefix, "share", "metainfo"))

    appstream_path = os.path.join(args.prefix, "share", "metainfo", "page.codeberg.JakobDev.jdMinecraftLauncher.metainfo.xml")

    subprocess.run(["msgfmt", "--desktop", "--template", os.path.join(project_root, "deploy", "page.codeberg.JakobDev.jdMinecraftLauncher.desktop"), "-d", os.path.join(project_root, "deploy", "translations"), "-o", os.path.join(args.prefix, "share", "applications", "page.codeberg.JakobDev.jdMinecraftLauncher.desktop")], check=True)
    subprocess.run(["msgfmt", "--xml", "--template", os.path.join(project_root, "deploy", "page.codeberg.JakobDev.jdMinecraftLauncher.metainfo.xml"), "-d", os.path.join(project_root, "deploy", "translations"), "-o", appstream_path], check=True)

    write_translation_status(project_root, appstream_path)


if __name__ == "__main__":
    main()
