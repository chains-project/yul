# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from mylib._compat import binary_type, text_type


def to_text(value, encoding="utf-8", errors="strict"):
    """Return ``value`` as a text (unicode) string on both Python 2 and 3."""
    if isinstance(value, text_type):
        return value
    if isinstance(value, binary_type):
        return value.decode(encoding, errors)
    return text_type(value)


def to_bytes(value, encoding="utf-8", errors="strict"):
    """Return ``value`` as a byte string on both Python 2 and 3."""
    if isinstance(value, binary_type):
        return value
    if not isinstance(value, text_type):
        value = text_type(value)
    return value.encode(encoding, errors)
