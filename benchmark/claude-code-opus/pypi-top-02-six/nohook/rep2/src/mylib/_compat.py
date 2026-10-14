"""Python 2/3 compatibility shims.

Keep every version check in this module so the rest of the code base can
import names from here instead of branching on the interpreter version.
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import sys

PY2 = sys.version_info[0] == 2

if PY2:  # pragma: no cover
    text_type = unicode  # noqa: F821
    binary_type = str
    string_types = (str, unicode)  # noqa: F821
    integer_types = (int, long)  # noqa: F821

    def iteritems(d, **kw):
        return d.iteritems(**kw)

else:
    text_type = str
    binary_type = bytes
    string_types = (str,)
    integer_types = (int,)

    def iteritems(d, **kw):
        return iter(d.items(**kw))


def ensure_text(s, encoding="utf-8", errors="strict"):
    """Coerce ``s`` to text (``unicode`` on Py2, ``str`` on Py3)."""
    if isinstance(s, binary_type):
        return s.decode(encoding, errors)
    if isinstance(s, text_type):
        return s
    raise TypeError("not expecting type '%s'" % type(s))


def ensure_binary(s, encoding="utf-8", errors="strict"):
    """Coerce ``s`` to bytes (``str`` on Py2, ``bytes`` on Py3)."""
    if isinstance(s, text_type):
        return s.encode(encoding, errors)
    if isinstance(s, binary_type):
        return s
    raise TypeError("not expecting type '%s'" % type(s))


def with_metaclass(meta, *bases):
    """Create a base class with a metaclass, using syntax valid on 2 and 3."""

    class metaclass(type):
        def __new__(cls, name, this_bases, d):
            return meta(name, bases, d)

    return type.__new__(metaclass, str("temporary_class"), (), {})
