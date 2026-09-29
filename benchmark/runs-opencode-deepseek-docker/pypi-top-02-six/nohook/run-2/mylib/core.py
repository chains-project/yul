from __future__ import absolute_import, division, print_function, unicode_literals

from ._compat import iteritems, string_types, text_type


def greet(name):
    if not isinstance(name, string_types):
        raise TypeError("name must be a string")
    return "Hello, {0}!".format(name)


def merge(*mappings):
    result = {}
    for mapping in mappings:
        for key, value in iteritems(mapping):
            result[key] = value
    return result


def normalize(text):
    if not isinstance(text, text_type):
        text = text.decode("utf-8")
    return " ".join(text.split()).strip()
