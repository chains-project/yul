# setup.py is kept (rather than a PEP 621 [project] table in pyproject.toml)
# because setuptools 44.x, the last release supporting Python 2.7, cannot read
# project metadata from pyproject.toml. All metadata lives in setup.cfg.
from setuptools import setup

setup()
