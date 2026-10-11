from __future__ import absolute_import, division, print_function, unicode_literals

import io
import os

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

about = {}
with io.open(os.path.join(here, "mylib", "__init__.py"), encoding="utf-8") as f:
    for line in f:
        if line.startswith("__version__"):
            about["__version__"] = line.split("=")[1].strip().strip("\"'")
            break

try:
    with io.open(os.path.join(here, "README.rst"), encoding="utf-8") as f:
        long_description = f.read()
except IOError:
    long_description = ""


setup(
    name="mylib",
    version=about["__version__"],
    description="A library that runs on both Python 2 and Python 3.",
    long_description=long_description,
    author="Your Name",
    author_email="you@example.com",
    url="https://github.com/example/mylib",
    license="MIT",
    packages=find_packages(exclude=("tests", "tests.*")),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "six>=1.12.0",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "tox>=3.24,<4",
            "flake8>=3.8,<4",
            "flake8-bugbear",
        ],
    },
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
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, <4",
)
