#!/usr/bin/env python3
import tempfile
import requests
import pathlib
import shutil
import pysftp
import os


SOURCEFORGE_PROJECT = "jdminecraftlauncher"
APPNAME = "jdMinecraftLauncher"

root_dir = str(pathlib.Path(__file__).parent.parent)
version = os.getenv("CI_COMMIT_TAG")


def create_new_dir(path: str):
    try:
        shutil.rmtree(path)
    except Exception:
        pass
    os.makedirs(path)


def create_source_zip():
     with tempfile.TemporaryDirectory() as workdir:
        shutil.copytree(os.path.join(root_dir, APPNAME), os.path.join(workdir, APPNAME))
        shutil.copyfile(os.path.join(root_dir,f"{APPNAME}.py"),os.path.join(workdir, f"{APPNAME}.py"))
        shutil.copyfile(os.path.join(root_dir, "README.md"),os.path.join(workdir, "README.md"))
        shutil.copyfile(os.path.join(root_dir, "LICENSE"),os.path.join(workdir, "LICENCE"))
        shutil.copyfile(os.path.join(root_dir, "requirements.txt"),os.path.join(workdir, "requirements.txt"))

        shutil.make_archive(os.path.join(root_dir, "output", f"{APPNAME}-{version}-Python"), "zip", workdir)


def upload_files():
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    server = pysftp.Connection(host="frs.sourceforge.net", username=os.getenv("SOURCEFORGE_USERNAME"), password=os.getenv("SOURCEFORGE_PASSWORD"), cnopts=cnopts)
    server.chdir(f"/home/frs/project/{SOURCEFORGE_PROJECT}")
    server.mkdir(version)
    server.chdir(f"/home/frs/project/{SOURCEFORGE_PROJECT}/{version}")
    for i in os.listdir(os.path.join(root_dir, "output")):
        server.put(os.path.join(root_dir, "output", i))
    server.close()

    requests.put(f"https://sourceforge.net/projects/{SOURCEFORGE_PROJECT}/files/{version}/{APPNAME}-{version}-Python.zip", {"default": "mac&default=linux&default=android&default=bsd&default=solaris&default=others", "api_key": os.getenv("SOURCEFORGE_API_KEY")},  headers={"Accept": "application/json"})
    requests.put(f"https://sourceforge.net/projects/{SOURCEFORGE_PROJECT}/files/{version}/{APPNAME}-{version}-WindowsInstaller.exe", {"default": "windows", "api_key": os.getenv("SOURCEFORGE_API_KEY")},  headers={"Accept": "application/json"})


def main():
    create_new_dir(os.path.join(root_dir, "output"))
    create_source_zip()
    shutil.make_archive(os.path.join(root_dir, "output", f"{APPNAME}-{version}-WindowsPortable"), "zip", os.path.join(root_dir, "WindowsBuild", "Portable"))
    shutil.copyfile(os.path.join(root_dir, "WindowsBuild", f"{APPNAME}Installer.exe"), os.path.join(root_dir, "output", f"{APPNAME}-{version}-WindowsInstaller.exe"))
    upload_files()


if __name__ == "__main__":
    main()
