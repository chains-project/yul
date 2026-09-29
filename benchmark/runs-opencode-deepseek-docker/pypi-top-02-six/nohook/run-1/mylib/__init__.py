"""A small example library written to run unchanged on Python 2 and Python 3."""

from __future__ import absolute_import

__version__ = "0.1.0"

from .core import decode, encode, greet, iter_dict, loads

__all__ = ["decode", "encode", "greet", "iter_dict", "loads", "__version__"]
