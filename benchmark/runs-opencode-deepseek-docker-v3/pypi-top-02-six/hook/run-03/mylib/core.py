# -*- coding: utf-8 -*-
"""Core functionality.

The module only uses constructs that behave identically under Python 2 and 3:
``from __future__`` imports, the ``_compat`` shims, and explicit text/bytes
handling.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import re

from mylib._compat import text_type

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(value):
    """Convert ``value`` into a lowercase, hyphen-separated slug.

    Works with both ``str``/``unicode`` input on Python 2 and ``str`` input on
    Python 3.
    """
    value = text_type(value).strip().lower()
    return _SLUG_RE.sub("-", value).strip("-")
