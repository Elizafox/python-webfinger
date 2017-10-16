#!/usr/bin/env python3

from setuptools import setup
from webfinger import __version__ as version

long_description = open('README.rst').read()

setup(name="webfinger2",
    version=version,
    packages=["webfinger"],
    description="Simple Python implementation of WebFinger client protocol",
    author="Jeremy Carbaugh, Elizabeth Myers",
    author_email="elizabeth@interlinked.me",
    license='BSD',
    url="http://github.com/jcarbaugh/python-webfinger/",
    long_description=long_description,
    install_requires=["requests", "defusedxml"],
    platforms=["any"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
