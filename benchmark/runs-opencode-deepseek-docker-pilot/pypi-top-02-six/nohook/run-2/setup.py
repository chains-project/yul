from __future__ import absolute_import, division, print_function

import io
import os

from setuptools import find_packages, setup

HERE = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(HERE, "README.rst"), encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()

about = {}
with io.open(os.path.join(HERE, "mylib", "_version.py"), encoding="utf-8") as f:
    exec(f.read(), about)

setup(
    name="mylib",
    version=about["__version__"],
    description="A sample library that supports both Python 2 and Python 3.",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/x-rst",
    url="https://github.com/example/mylib",
    license="MIT",
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    zip_safe=False,
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    install_requires=[],
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
)
