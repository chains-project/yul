# -*- coding: utf-8 -*-
"""Python 2/3 compatibility shims.

Keep all version checks in this module so the rest of the package can be
written once, against these names.
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import sys

PY2 = sys.version_info[0] == 2

if PY2:  # pragma: no cover
    text_type = unicode  # noqa: F821
    binary_type = str
    string_types = (str, unicode)  # noqa: F821
    integer_types = (int, long)  # noqa: F821
    from itertools import izip as zip  # noqa: F401
    from urllib import quote, unquote  # noqa: F401
    from urlparse import urlparse  # noqa: F401

    def iteritems(d):
        return d.iteritems()
else:
    text_type = str
    binary_type = bytes
    string_types = (str,)
    integer_types = (int,)
    zip = zip
    from urllib.parse import quote, unquote, urlparse  # noqa: F401

    def iteritems(d):
        return iter(d.items())


def to_text(value, encoding="utf-8", errors="strict"):
    """Return ``value`` as a text (unicode) string."""
    if isinstance(value, binary_type):
        return value.decode(encoding, errors)
    if isinstance(value, text_type):
        return value
    return text_type(value)


def to_bytes(value, encoding="utf-8", errors="strict"):
    """Return ``value`` as a byte string."""
    if isinstance(value, text_type):
        return value.encode(encoding, errors)
    if isinstance(value, binary_type):
        return value
    return to_text(value).encode(encoding, errors)


def with_metaclass(meta, *bases):
    """Create a base class with a metaclass (works on both 2 and 3)."""

    class _Meta(meta):
        def __new__(mcs, name, this_bases, d):
            return meta(name, bases, d)

    return type.__new__(_Meta, str("temporary_class"), (), {})
