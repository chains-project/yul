from __future__ import absolute_import, division, print_function, unicode_literals

import io
import os
import re

from setuptools import find_packages, setup


HERE = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with io.open(os.path.join(HERE, *parts), encoding="utf-8") as handle:
        return handle.read()


def find_version(*parts):
    version_file = read(*parts)
    match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if not match:
        raise RuntimeError("Unable to find version string.")
    return match.group(1)


setup(
    name="mylib",
    version=find_version("mylib", "__init__.py"),
    description="A library that supports both Python 2 and Python 3.",
    long_description=read("README.rst"),
    long_description_content_type="text/x-rst",
    author="Your Name",
    author_email="you@example.com",
    url="https://example.com/mylib",
    license="MIT",
    packages=find_packages(exclude=("tests", "tests.*")),
    install_requires=[
        "six>=1.12.0",
    ],
    extras_require={
        "test": [
            "pytest",
            "pytest-cov",
        ],
    },
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries",
    ],
    keywords="mylib example python2 python3",
    zip_safe=False,
)
