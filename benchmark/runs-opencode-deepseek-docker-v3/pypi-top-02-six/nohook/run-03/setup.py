# -*- coding: utf-8 -*-
"""Packaging configuration for mylib.

This file must be importable by Python 2.7 *and* Python 3, so it avoids
f-strings, keyword-only arguments and any other 3-only syntax.
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import io
import os

from setuptools import find_packages, setup

HERE = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    """Read a UTF-8 encoded file relative to this setup.py."""
    with io.open(os.path.join(HERE, *parts), encoding="utf-8") as handle:
        return handle.read()


TEST_REQUIRES = ["pytest"]
# unittest.mock only exists on Python 3; the backport is needed on Python 2.
try:
    import unittest.mock  # noqa: F401
except ImportError:
    TEST_REQUIRES.append("mock")

setup(
    name="mylib",
    version="0.1.0",
    description="A library whose source is compatible with Python 2 and Python 3.",
    long_description=read("README.rst"),
    long_description_content_type="text/x-rst",
    author="mylib authors",
    author_email="maintainers@example.com",
    url="https://example.com/mylib",
    license="MIT",
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
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="python2 python3 compatibility library",
    packages=find_packages(exclude=["tests", "tests.*"]),
    # six is the canonical compatibility shim across the 2/3 divide.
    install_requires=["six >= 1.10"],
    extras_require={
        "test": TEST_REQUIRES,
    },
    # Refuse to install on interpreters we do not support.
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*",
    zip_safe=False,
)
