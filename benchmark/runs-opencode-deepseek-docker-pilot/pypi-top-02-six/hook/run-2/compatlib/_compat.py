"""Python 2/3 compatibility helpers.

Import from this module rather than branching on :data:`sys.version_info` at
every call site.  The public names mirror the most frequently used parts of
the ``six`` library, but without the dependency.
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import sys

PY2 = sys.version_info[0] == 2

if PY2:
    string_types = (basestring,)  # noqa: F821  (Python 2 builtin)
    text_type = unicode  # noqa: F821
    binary_type = str
    integer_types = (int, long)  # noqa: F821
else:
    string_types = (str,)
    text_type = str
    binary_type = bytes
    integer_types = (int,)


def iteritems(mapping):
    """Return an iterator over the ``(key, value)`` pairs of *mapping*."""
    return iter(mapping.items())


def itervalues(mapping):
    """Return an iterator over the values of *mapping*."""
    return iter(mapping.values())


def to_bytes(value, encoding="utf-8", errors="strict"):
    """Return *value* as :data:`binary_type` on the current interpreter."""
    if isinstance(value, binary_type):
        return value
    if isinstance(value, text_type):
        return value.encode(encoding, errors)
    raise TypeError("expected str or bytes, got %s" % type(value).__name__)


def to_text(value, encoding="utf-8", errors="strict"):
    """Return *value* as :data:`text_type` on the current interpreter."""
    if isinstance(value, text_type):
        return value
    if isinstance(value, binary_type):
        return value.decode(encoding, errors)
    raise TypeError("expected str or bytes, got %s" % type(value).__name__)
