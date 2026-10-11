"""Compatibility shims for code that must run on Python 2 and Python 3.

Import names from this module instead of relying on version-specific
builtins so the rest of the codebase can stay version agnostic.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import sys

PY2 = sys.version_info[0] == 2

if PY2:  # pragma: no cover - exercised only on Python 2
    import __builtin__ as builtins
    from StringIO import StringIO
    from itertools import ifilter as filter
    from itertools import imap as map
    from itertools import izip as zip
    from urllib2 import Request, urlopen

    text_type = unicode  # noqa: F821
    binary_type = str
    string_types = (basestring,)  # noqa: F821
    integer_types = (int, long)  # noqa: F821
    range = xrange  # noqa: F821

    def iteritems(d, **kw):
        return d.iteritems(**kw)

    def iterkeys(d, **kw):
        return d.iterkeys(**kw)

    def itervalues(d, **kw):
        return d.itervalues(**kw)

    def iterbytes(b):
        return (ord(c) for c in b)

else:  # pragma: no cover - exercised only on Python 3
    import builtins
    from io import StringIO
    from urllib.request import Request, urlopen

    text_type = str
    binary_type = bytes
    string_types = (str,)
    integer_types = (int,)
    range = range

    def iteritems(d, **kw):
        return iter(d.items(**kw))

    def iterkeys(d, **kw):
        return iter(d.keys(**kw))

    def itervalues(d, **kw):
        return iter(d.values(**kw))

    def iterbytes(b):
        return iter(b)


__all__ = [
    "PY2",
    "builtins",
    "StringIO",
    "Request",
    "urlopen",
    "filter",
    "map",
    "zip",
    "range",
    "text_type",
    "binary_type",
    "string_types",
    "integer_types",
    "iteritems",
    "iterkeys",
    "itervalues",
    "iterbytes",
]
