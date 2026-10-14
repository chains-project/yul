"""Python 2/3 compatibility shims.

Keep every version check in this module so the rest of the package can be
written once against these names.
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import sys

PY2 = sys.version_info[0] == 2

if PY2:  # pragma: no cover
    text_type = unicode  # noqa: F821
    binary_type = str
    string_types = (str, unicode)  # noqa: F821
    integer_types = (int, long)  # noqa: F821
    from StringIO import StringIO  # noqa: F401
    from itertools import izip as zip  # noqa: F401
else:
    text_type = str
    binary_type = bytes
    string_types = (str,)
    integer_types = (int,)
    from io import StringIO  # noqa: F401
    zip = zip


def ensure_text(value, encoding="utf-8", errors="strict"):
    """Return ``value`` as text (``unicode`` on 2, ``str`` on 3)."""
    if isinstance(value, text_type):
        return value
    if isinstance(value, binary_type):
        return value.decode(encoding, errors)
    raise TypeError("expected bytes or text, got %r" % type(value))


def ensure_binary(value, encoding="utf-8", errors="strict"):
    """Return ``value`` as bytes (``str`` on 2, ``bytes`` on 3)."""
    if isinstance(value, binary_type):
        return value
    if isinstance(value, text_type):
        return value.encode(encoding, errors)
    raise TypeError("expected bytes or text, got %r" % type(value))
