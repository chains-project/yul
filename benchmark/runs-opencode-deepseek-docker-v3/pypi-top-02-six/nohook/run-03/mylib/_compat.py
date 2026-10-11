# -*- coding: utf-8 -*-
"""Central place for everything that differs between Python 2 and Python 3.

All other modules import from here instead of branching on ``sys.version``
directly. That keeps the compatibility logic in one reviewable place.
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import sys

import six

PY2 = sys.version_info[0] == 2
PY3 = not PY2

# Type tuples that are safe to use with isinstance() on both major versions.
string_types = six.string_types
text_type = six.text_type
binary_type = six.binary_type
integer_types = six.integer_types

# stdlib modules whose location/name changed between 2 and 3.
from six.moves import configparser  # noqa: E402,F401
from six.moves import queue  # noqa: E402,F401
from six.moves import urllib_parse  # noqa: E402,F401

__all__ = [
    "PY2",
    "PY3",
    "string_types",
    "text_type",
    "binary_type",
    "integer_types",
    "configparser",
    "queue",
    "urllib_parse",
]
