# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from mylib._compat import to_text


def greet(name):
    """Return a greeting for ``name`` as text, accepting bytes or text."""
    return u"Hello, {0}!".format(to_text(name))
