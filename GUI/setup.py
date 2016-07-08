# -*- coding: utf-8 -*-
"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ['dropbox_cargo.py']
DATA_FILES = ['CargoLift.xib']
OPTIONS = {
	'argv_emulation': True,
	'iconfile': 'dropbox.icns',
	'plist': {
        'CFBundleName': 'CargoLift',
        'CFBundleDisplayName': 'CargoLift',
        'CFBundleGetInfoString': "Upload file or folder to Dropbox and get share link",
        'CFBundleIdentifier': "benbenbang",
        'CFBundleVersion': "0.1.0",
        'CFBundleShortVersionString': "0.1.0",
        'NSHumanReadableCopyright': u"Copyright © 2016, Ben Chen, All Rights Reserved"
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
