"""mylib: a library compatible with Python 2.7 and Python 3."""
from __future__ import absolute_import, division, print_function, unicode_literals

from mylib.core import greet

__version__ = "0.1.0"
__all__ = ["greet", "__version__"]
