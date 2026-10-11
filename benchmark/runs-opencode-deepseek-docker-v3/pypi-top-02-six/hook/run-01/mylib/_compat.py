"""Compatibility helpers shared by Python 2 and Python 3 code.

Importing the primitives below (rather than referencing ``str``, ``unicode``,
``bytes`` or the iterator builtins directly) keeps the rest of the package
portable.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import sys

PY2 = sys.version_info[0] == 2

if PY2:  # pragma: no cover - executed on Python 2 only
    text_type = unicode  # noqa: F821
    binary_type = str
    string_types = (basestring,)  # noqa: F821
    integer_types = (int, long)  # noqa: F821

    from itertools import imap as map  # noqa: F401
    from itertools import izip as zip  # noqa: F401
    from urllib2 import urlopen  # noqa: F401
else:  # pragma: no cover - executed on Python 3 only
    text_type = str
    binary_type = bytes
    string_types = (str,)
    integer_types = (int,)

    from builtins import map, zip  # noqa: F401
    from urllib.request import urlopen  # noqa: F401


def to_unicode(value, encoding="utf-8", errors="strict"):
    """Return *value* as text, decoding bytes when necessary."""
    if isinstance(value, text_type):
        return value
    if isinstance(value, binary_type):
        return value.decode(encoding, errors)
    return text_type(value)


def to_bytes(value, encoding="utf-8", errors="strict"):
    """Return *value* as bytes, encoding text when necessary."""
    if isinstance(value, binary_type):
        return value
    if isinstance(value, text_type):
        return value.encode(encoding, errors)
    return binary_type(value)
