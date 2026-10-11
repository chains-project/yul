"""mylib: a library compatible with Python 2 and Python 3."""

from __future__ import absolute_import, unicode_literals

from .core import greet, merge

__all__ = ["greet", "merge"]

__version__ = "0.1.0"
