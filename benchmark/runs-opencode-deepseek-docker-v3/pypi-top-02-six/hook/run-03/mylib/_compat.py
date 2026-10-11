# -*- coding: utf-8 -*-
"""Compatibility helpers shared across Python 2 and Python 3.

Keeping the version differences in one module means the rest of the codebase
can be written the same way regardless of the interpreter running it.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import sys

import six

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

string_types = six.string_types
text_type = six.text_type
binary_type = six.binary_type
integer_types = six.integer_types

iteritems = six.iteritems
itervalues = six.itervalues
iterkeys = six.iterkeys

text = six.text_type
binary = six.binary_type

if PY3:
    from urllib.parse import quote, unquote, urlparse
else:  # pragma: no cover - exercised only on Python 2
    from urllib import quote, unquote  # noqa: F401
    from urlparse import urlparse  # noqa: F401


def to_text(value, encoding="utf-8", errors="strict"):
    """Return ``value`` as ``unicode`` on Python 2 and ``str`` on Python 3."""
    if isinstance(value, text_type):
        return value
    if isinstance(value, binary_type):
        return value.decode(encoding, errors)
    return text_type(value)


def to_bytes(value, encoding="utf-8", errors="strict"):
    """Return ``value`` as ``bytes`` on both Python 2 and Python 3."""
    if isinstance(value, binary_type):
        return value
    if not isinstance(value, text_type):
        value = text_type(value)
    return value.encode(encoding, errors)
