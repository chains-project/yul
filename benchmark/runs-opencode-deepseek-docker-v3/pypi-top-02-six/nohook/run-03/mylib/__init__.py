# -*- coding: utf-8 -*-
"""mylib: a small library that runs unchanged on Python 2 and Python 3.

Import the public helpers from the top level::

    >>> from mylib import ensure_bytes, ensure_text
    >>> ensure_text(b"caf\\xc3\\xa9")
    u'caf\xe9'

"""
from __future__ import absolute_import, division, print_function, unicode_literals

from ._compat import PY2, PY3
from .core import ensure_bytes, ensure_text, python_version

__all__ = ["PY2", "PY3", "ensure_bytes", "ensure_text", "python_version"]

__version__ = "0.1.0"
