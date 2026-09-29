# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from .compat import binary_type, iteritems, text_type


def to_text(value, encoding="utf-8"):
    if isinstance(value, text_type):
        return value
    if isinstance(value, binary_type):
        return value.decode(encoding)
    return text_type(value)


def to_bytes(value, encoding="utf-8"):
    if isinstance(value, binary_type):
        return value
    if isinstance(value, text_type):
        return value.encode(encoding)
    return text_type(value).encode(encoding)


def greet(name):
    if not isinstance(name, (text_type, binary_type)):
        raise TypeError("name must be a string, got %r" % (type(name),))
    return "Hello, {0}!".format(to_text(name))


def merged(*mappings):
    result = {}
    for mapping in mappings:
        for key, value in iteritems(mapping):
            result[key] = value
    return result
