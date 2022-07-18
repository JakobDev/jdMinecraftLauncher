#!/usr/bin/env python3
from setuptools import find_packages, setup
import os


with open(os.path.join(os.path.dirname(__file__), "jdMinecraftLauncher", "version.txt"), "r", encoding="utf-8") as f:
    version = f.read().strip()

with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()


setup(name='jdMinecraftLauncher',
    version=version,
    description='A Minecraft Launcher writen in Python',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='JakobDev',
    author_email='jakobdev@gmx.de',
    url='https://gitlab.com/JakobDev/jdMinecraftLauncher',
    download_url='https://gitlab.com/JakobDev/jdMinecraftLauncher/-/releases',
    python_requires='>=3.8',
    include_package_data=True,
    install_requires=[
        'PyQt6',
        'PyQt6-WebEngine',
        'requests',
        'minecraft-launcher-lib',
        'jdTranslationHelper'
    ],
    packages=find_packages(),
    entry_points={
        'console_scripts': ['jdMinecraftLauncher = jdMinecraftLauncher.jdMinecraftLauncher:main']
    },
    license='GPL v3',
    keywords=['JakobDev','Minecraft','Mojang','Java','PyQt','PyQt5'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: End Users/Desktop',
        'Environment :: Other Environment',
        'Environment :: X11 Applications :: Qt',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Natural Language :: German',
        'Operating System :: OS Independent',
        "Operating System :: POSIX",
        "Operating System :: POSIX :: BSD",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
 )

