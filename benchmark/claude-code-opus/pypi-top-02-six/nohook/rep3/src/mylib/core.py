# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from mylib._compat import to_text


def greet(name):
    """Return a greeting for ``name`` (bytes or text) as a text string."""
    return "Hello, {0}!".format(to_text(name))
