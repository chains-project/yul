from __future__ import absolute_import, division, print_function, unicode_literals

import io
import os

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))


def read(path):
    with io.open(os.path.join(here, path), encoding="utf-8") as handle:
        return handle.read()


long_description = read("README.rst")

setup(
    name="mylib",
    version="0.1.0",
    description="A small library that supports both Python 2 and Python 3.",
    long_description=long_description,
    author="Example Author",
    author_email="author@example.com",
    url="https://github.com/example/mylib",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    keywords="library python2 python3 six",
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=[
        "six>=1.12.0",
    ],
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*",
    extras_require={
        "dev": ["pytest", "tox", "flake8"],
    },
    zip_safe=False,
)
