"""Example functionality that is identical under Python 2 and Python 3.

The functions here avoid version specific ``str``/``bytes`` behaviour by
always converting through :mod:`mylib.compat`.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import base64
import json

from .compat import binary_type, iteritems, string_types, to_bytes, to_text

_STRING_TYPES = string_types + (binary_type,)

__all__ = ["greet", "encode", "decode", "loads", "iter_dict"]


def greet(name):
    """Return a friendly greeting for *name*.

    ``name`` may be a byte string or a text string on either interpreter;
    the result is always a text string.
    """
    if not isinstance(name, _STRING_TYPES):
        raise TypeError("name must be a string")
    return "Hello, {0}!".format(to_text(name))


def encode(data):
    """Base64 encode *data* and return the result as text.

    Accepting and returning text keeps the value identical on Python 2 and
    Python 3, where ``base64`` otherwise straddles ``str`` and ``bytes``.
    """
    return to_text(base64.b64encode(to_bytes(data)))


def decode(data):
    """Reverse :func:`encode`, returning the decoded value as text."""
    return to_text(base64.b64decode(to_bytes(data)))


def loads(data):
    """Deserialize a JSON document from bytes or text."""
    return json.loads(to_text(data))


def iter_dict(mapping):
    """Iterate over the ``(key, value)`` pairs of *mapping* efficiently.

    On Python 2 this avoids materialising a list as ``dict.items`` would.
    """
    return iteritems(mapping)
