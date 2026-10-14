# -*- coding: utf-8 -*-
"""Python 2/3 compatibility shims.

Keep all version checks in this module so the rest of the package can import
names from here instead of branching on ``sys.version_info`` everywhere.
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import sys

PY2 = sys.version_info[0] == 2
PY3 = not PY2

if PY2:  # pragma: no cover
    text_type = unicode  # noqa: F821
    binary_type = str
    string_types = (str, unicode)  # noqa: F821
    integer_types = (int, long)  # noqa: F821

    from itertools import izip as zip  # noqa: F401
    from StringIO import StringIO  # noqa: F401
    from urlparse import urljoin, urlparse  # noqa: F401

    def iteritems(d, **kw):
        return d.iteritems(**kw)

else:
    text_type = str
    binary_type = bytes
    string_types = (str,)
    integer_types = (int,)

    zip = zip
    from io import StringIO  # noqa: F401
    from urllib.parse import urljoin, urlparse  # noqa: F401

    def iteritems(d, **kw):
        return iter(d.items(**kw))
