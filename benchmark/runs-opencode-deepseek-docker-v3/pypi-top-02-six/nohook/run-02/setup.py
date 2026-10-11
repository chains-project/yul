from __future__ import absolute_import, print_function

import io
import os

from setuptools import find_packages, setup

HERE = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(HERE, "README.rst"), encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()

setup(
    name="mylib",
    version="0.1.0",
    description="A library that supports both Python 2 and Python 3.",
    long_description=LONG_DESCRIPTION,
    author="Your Name",
    author_email="you@example.com",
    url="https://github.com/your-org/mylib",
    license="MIT",
    packages=find_packages(exclude=["tests", "tests.*"]),
    # setuptools >= 24.2 understands python_requires; older versions ignore it.
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    install_requires=[],
    extras_require={
        "test": ["pytest<5; python_version<'3'", "pytest; python_version>='3'"],
    },
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
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
