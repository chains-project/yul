from __future__ import absolute_import, division, print_function, unicode_literals

from ._compat import string_types

DEFAULT_GREETING = "Hello"


def greet(name, greeting=DEFAULT_GREETING):
    if not isinstance(name, string_types):
        raise TypeError(
            "name must be a string, got {0}".format(type(name).__name__)
        )
    return "{0}, {1}!".format(greeting, name)


def utf8_len(text):
    if isinstance(text, bytes):
        return len(text)
    return len(text.encode("utf-8"))
