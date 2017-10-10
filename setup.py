#!/usr/bin/env python3

from setuptools import setup
from webfinger import __version__

long_description = open('README.rst').read()

setup(name="webfinger2",
    version=__version__,
    py_modules=["webfinger"],
    description="Simple Python implementation of WebFinger client protocol",
    author="Jeremy Carbaugh, Elizabeth Myers",
    author_email="elizabeth@interlinked.me",
    license='BSD',
    url="http://github.com/jcarbaugh/python-webfinger/",
    long_description=long_description,
    install_requires=["requests"],
    platforms=["any"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
