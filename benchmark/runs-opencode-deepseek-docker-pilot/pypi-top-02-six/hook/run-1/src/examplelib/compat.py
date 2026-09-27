# -*- coding: utf-8 -*-
"""Compatibility helpers shared by Python 2 and Python 3.

Import everything that differs between the two runtimes from here instead of
branching on :data:`six.PY3` throughout the code base.
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import six

__all__ = [
    'PY2',
    'PY3',
    'string_types',
    'text_type',
    'binary_type',
    'integer_types',
    'iteritems',
    'itervalues',
    'iterkeys',
]

PY2 = six.PY2
PY3 = six.PY3

string_types = six.string_types
text_type = six.text_type
binary_type = six.binary_type
integer_types = six.integer_types

iteritems = six.iteritems
itervalues = six.itervalues
iterkeys = six.iterkeys
