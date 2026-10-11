"""Compatibility helpers shared across Python 2.7 and Python 3.x.

Everything version-specific lives here so the rest of the package can import
from a single module instead of sprinkling ``sys.version_info`` checks around.
The implementation delegates to :mod:`six`, which handles the subtle cases
(``unicode`` vs ``str``, ``__metaclass__``, byte iteration, ...).
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import sys

import six

__all__ = [
    "PY2",
    "PY3",
    "binary_type",
    "integer_types",
    "iteritems",
    "iterkeys",
    "itervalues",
    "string_types",
    "text_type",
    "to_bytes",
    "to_native",
    "to_text",
    "urlencode",
    "unichr",
    "with_metaclass",
    "zip_longest",
]


PY2 = sys.version_info[0] == 2
PY3 = not PY2

string_types = six.string_types
text_type = six.text_type
binary_type = six.binary_type
integer_types = six.integer_types
unichr = six.unichr
with_metaclass = six.with_metaclass
urlencode = six.moves.urllib.parse.urlencode
zip_longest = six.moves.zip_longest

iteritems = six.iteritems
iterkeys = six.iterkeys
itervalues = six.itervalues


def to_bytes(value, encoding="utf-8", errors="strict"):
    """Return ``value`` encoded as a native ``bytes`` object."""
    if isinstance(value, binary_type):
        return value
    if isinstance(value, text_type):
        return value.encode(encoding, errors)
    return text_type(value).encode(encoding, errors)


def to_text(value, encoding="utf-8", errors="strict"):
    """Return ``value`` decoded to a native ``unicode``/``str`` object."""
    if isinstance(value, text_type):
        return value
    if isinstance(value, binary_type):
        return value.decode(encoding, errors)
    return text_type(value)


def to_native(value, encoding="utf-8", errors="strict"):
    """Return ``value`` as the native ``str`` type for the running interpreter.

    On Python 2 that is ``bytes``; on Python 3 that is ``unicode`` text.
    """
    if PY2:
        return to_bytes(value, encoding, errors)
    return to_text(value, encoding, errors)
