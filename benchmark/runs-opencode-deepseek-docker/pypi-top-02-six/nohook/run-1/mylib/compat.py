"""Thin compatibility layer shared by the rest of the package.

Everything that differs between Python 2 and Python 3 is funnelled through
this module so the rest of the code base can stay version agnostic. The
heavy lifting is delegated to :mod:`six`.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import sys

import six

PY2 = sys.version_info[0] == 2
PY3 = not PY2

text_type = six.text_type
binary_type = six.binary_type
string_types = six.string_types
integer_types = six.integer_types

iteritems = six.iteritems
iterkeys = six.iterkeys
itervalues = six.itervalues

add_metaclass = six.add_metaclass
with_metaclass = six.with_metaclass
reraise = six.reraise


def to_bytes(value, encoding="utf-8"):
    """Return *value* as ``bytes`` on both Python 2 and Python 3."""
    if isinstance(value, binary_type):
        return value
    if isinstance(value, text_type):
        return value.encode(encoding)
    raise TypeError("expected a string, got {0}".format(type(value).__name__))


def to_text(value, encoding="utf-8"):
    """Return *value* as text (``unicode`` on Python 2, ``str`` on Python 3)."""
    if isinstance(value, text_type):
        return value
    if isinstance(value, binary_type):
        return value.decode(encoding)
    raise TypeError("expected a string, got {0}".format(type(value).__name__))
