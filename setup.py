"""
Setup.py for FFs
"""
import os
import re
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

HERE = os.path.realpath(os.path.dirname(__file__))

VERSION_FILE = os.path.join(HERE, "onsapi/_version.py")
verstrline = open(VERSION_FILE, "rt").read()
VSRE = r'^__version__ = [\'"]([^\'"]*)[\'"]'
mo = re.search(VSRE,  verstrline, re.M)
if mo:
    VERSION = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in {0}".format(VERSION_FILE))

os.chdir(HERE)

install_requires = ['requests', 'cached-property']
if sys.version_info < (2, 6):
    install_requires.append('smplejson')

setup(
    name="onsapi",
    version=VERSION,
    author="Fred Kingham",
    author_email="fredkingham@gmail.com",
    description="Simple python api for the ons",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 3.1",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries"
        ],
    install_requires=install_requires,
    packages=['onsapi'],
)
