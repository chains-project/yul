from __future__ import absolute_import, division, print_function, unicode_literals

import sys

PY2 = sys.version_info[0] == 2

if PY2:
    text_type = unicode
    binary_type = str
    string_types = (basestring,)
    integer_types = (int, long)
    from itertools import imap as map
    from itertools import izip as zip
    from urllib2 import Request, urlopen
    from urlparse import urlparse
else:
    text_type = str
    binary_type = bytes
    string_types = (str,)
    integer_types = (int,)
    map = map
    zip = zip
    from urllib.request import Request, urlopen
    from urllib.parse import urlparse


def to_unicode(value, encoding="utf-8", errors="strict"):
    if isinstance(value, text_type):
        return value
    if isinstance(value, binary_type):
        return value.decode(encoding, errors)
    return text_type(value)


def to_bytes(value, encoding="utf-8", errors="strict"):
    if isinstance(value, binary_type):
        return value
    if isinstance(value, text_type):
        return value.encode(encoding, errors)
    return binary_type(value)


if PY2:
    def iteritems(mapping):
        return mapping.iteritems()
else:
    def iteritems(mapping):
        return iter(mapping.items())
