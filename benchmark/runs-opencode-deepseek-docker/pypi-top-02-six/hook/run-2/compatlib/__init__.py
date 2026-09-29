"""A library whose source runs on both Python 2 and Python 3."""
from __future__ import absolute_import, division, print_function, unicode_literals

from ._compat import PY2, binary_type, integer_types, iteritems, string_types
from ._compat import text_type, to_bytes, to_text
from .core import greet, read_text, write_text

__version__ = "0.1.0"

__all__ = [
    "PY2",
    "binary_type",
    "greet",
    "integer_types",
    "iteritems",
    "read_text",
    "string_types",
    "text_type",
    "to_bytes",
    "to_text",
    "write_text",
    "__version__",
]
