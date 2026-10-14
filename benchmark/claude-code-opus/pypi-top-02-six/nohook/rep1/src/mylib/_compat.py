# -*- coding: utf-8 -*-
"""Python 2/3 compatibility shims.

Keep every version-specific branch in this module so the rest of the
package can be written once and import names from here.
"""
from __future__ import absolute_import, division, print_function

import sys

PY2 = sys.version_info[0] == 2

if PY2:  # pragma: no cover
    text_type = unicode  # noqa: F821
    binary_type = str
    string_types = (str, unicode)  # noqa: F821
    integer_types = (int, long)  # noqa: F821  # novm

    def iteritems(d):
        return d.iteritems()
else:
    text_type = str
    binary_type = bytes
    string_types = (str,)
    integer_types = (int,)

    def iteritems(d):
        return iter(d.items())


def to_text(value, encoding="utf-8", errors="strict"):
    """Return ``value`` as text (``unicode`` on Py2, ``str`` on Py3)."""
    if isinstance(value, binary_type):
        return value.decode(encoding, errors)
    return text_type(value)


def to_bytes(value, encoding="utf-8", errors="strict"):
    """Return ``value`` as bytes (``str`` on Py2, ``bytes`` on Py3)."""
    if isinstance(value, text_type):
        return value.encode(encoding, errors)
    return binary_type(value)
