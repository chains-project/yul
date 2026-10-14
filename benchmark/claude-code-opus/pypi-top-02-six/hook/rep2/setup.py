# Metadata lives in setup.cfg. This shim exists for older pip/setuptools on
# Python 2.7, which cannot build from pyproject.toml alone.
from setuptools import setup

setup()
