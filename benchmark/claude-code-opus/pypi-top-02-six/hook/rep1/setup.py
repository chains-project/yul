# -*- coding: utf-8 -*-
import io
import os
import re

from setuptools import find_packages, setup

HERE = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with io.open(os.path.join(HERE, *parts), encoding="utf-8") as f:
        return f.read()


def find_version(*parts):
    match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]", read(*parts), re.M
    )
    if not match:
        raise RuntimeError("Unable to find version string.")
    return match.group(1)


setup(
    name="mylib",
    version=find_version("src", "mylib", "__init__.py"),
    description="A library compatible with Python 2.7 and Python 3.",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    zip_safe=False,
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*",
    install_requires=[],
    extras_require={
        # pip resolves pytest 4.6.x on Python 2.7 via pytest's python_requires.
        "test": ["pytest>=4.6"],
    },
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
    ],
)
