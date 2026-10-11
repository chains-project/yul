# -*- coding: utf-8 -*-
"""Example public API showing the idioms used across the library."""
from __future__ import absolute_import, division, print_function, unicode_literals

import sys

from ._compat import binary_type, string_types, text_type

DEFAULT_ENCODING = "utf-8"


def ensure_text(value, encoding=DEFAULT_ENCODING, errors="strict"):
    """Return *value* as ``unicode``/``str`` text.

    On Python 2 this yields ``unicode`` and on Python 3 plain ``str``.
    """
    if isinstance(value, text_type):
        return value
    if isinstance(value, binary_type):
        return value.decode(encoding, errors)
    raise TypeError(
        "expected a string, got {0!r}".format(type(value).__name__)
    )


def ensure_bytes(value, encoding=DEFAULT_ENCODING, errors="strict"):
    """Return *value* as ``bytes`` on both Python 2 and Python 3."""
    if isinstance(value, binary_type):
        return value
    if isinstance(value, text_type):
        return value.encode(encoding, errors)
    raise TypeError(
        "expected a string, got {0!r}".format(type(value).__name__)
    )


def is_string(value):
    """True for both text and byte strings on either major version.

    ``six.string_types`` is text-only on Python 3 (``(str,)``) but covers
    ``str`` *and* ``unicode`` on Python 2, so bytes are checked explicitly.
    """
    return isinstance(value, string_types) or isinstance(value, binary_type)


def python_version():
    """Return the running interpreter version as a 2-tuple of ints."""
    return (sys.version_info[0], sys.version_info[1])
