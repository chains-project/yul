# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import io
import os
import re

from setuptools import find_packages, setup

HERE = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with io.open(os.path.join(HERE, *parts), "r", encoding="utf-8") as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if match:
        return match.group(1)
    raise RuntimeError("Unable to find version string in %s." % (file_paths,))


setup(
    name="mylib",
    version=find_version("src", "mylib", "__init__.py"),
    description="A library that runs on both Python 2 and Python 3.",
    long_description=read("README.rst"),
    long_description_content_type="text/x-rst",
    author="Your Name",
    author_email="you@example.com",
    url="https://github.com/yourname/mylib",
    license="MIT",
    package_dir={"": "src"},
    packages=find_packages("src"),
    include_package_data=True,
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    install_requires=[
        "six>=1.10",
    ],
    extras_require={
        ":python_version<'3.4'": ["enum34", "pathlib2"],
        "tests": ["pytest", "pytest-cov"],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="example library python2 python3 compatibility six",
    zip_safe=False,
)
