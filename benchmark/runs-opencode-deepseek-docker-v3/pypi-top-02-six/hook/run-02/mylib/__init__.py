"""mylib - a library that runs unchanged on Python 2 and Python 3.

The public API lives in :mod:`mylib.core`.  Compatibility helpers are kept
private in :mod:`mylib._compat` so the rest of the code base can be written
against a single, consistent set of names.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

from ._compat import iteritems
from .core import chunked, slugify

__all__ = ["chunked", "iteritems", "slugify", "__version__"]

__version__ = "0.1.0"
