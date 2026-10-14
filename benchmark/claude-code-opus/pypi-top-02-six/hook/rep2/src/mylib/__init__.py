# -*- coding: utf-8 -*-
"""mylib: a library supporting both Python 2.7 and Python 3."""
from __future__ import absolute_import, division, print_function

from mylib._compat import to_bytes, to_text

__version__ = "0.1.0"

__all__ = ["to_bytes", "to_text", "__version__"]
