#!/usr/bin/env python3
from setuptools import find_packages, setup

setup(name='jdMinecraftLauncher',
    version='3.1',
    description='A Minecraft Launcher writen in Python',
    long_description=open("README.md").read(),
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
        'jdTranslationHelper',
        'cryptography'
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

