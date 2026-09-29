#!/usr/bin/env python
"""Setup script for mylib, installable under Python 2 and Python 3."""

from __future__ import absolute_import, print_function

import io
import os
import re

from setuptools import find_packages, setup

HERE = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with io.open(os.path.join(HERE, *parts), encoding="utf-8") as handle:
        return handle.read()


def find_version(*parts):
    match = re.search(
        r"^__version__\s*=\s*['\"]([^'\"]+)['\"]",
        read(*parts),
        re.MULTILINE,
    )
    if not match:
        raise RuntimeError("Unable to find __version__ string")
    return match.group(1)


setup(
    name="mylib",
    version=find_version("mylib", "__init__.py"),
    description="Example library that runs unchanged on Python 2 and Python 3",
    long_description=read("README.rst"),
    long_description_content_type="text/x-rst",
    author="mylib authors",
    author_email="mylib@example.com",
    url="https://github.com/example/mylib",
    license="MIT",
    packages=find_packages(exclude=("tests", "tests.*")),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "six>=1.10.0",
    ],
    extras_require={
        "test": [
            "pytest>=3.0",
        ],
    },
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="example compatibility python2 python3",
)
