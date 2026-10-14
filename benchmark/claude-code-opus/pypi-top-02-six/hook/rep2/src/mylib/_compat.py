# -*- coding: utf-8 -*-
"""Helpers for code that runs on both Python 2 and Python 3.

Use ``six`` for most compatibility needs (``six.text_type``,
``six.moves``, ``six.add_metaclass``, ...). Put small project-specific
shims here so the rest of the package doesn't branch on the version.
"""
from __future__ import absolute_import, division, print_function

import six


def to_text(value, encoding="utf-8", errors="strict"):
    """Return *value* as text (``unicode`` on Py2, ``str`` on Py3)."""
    if isinstance(value, six.text_type):
        return value
    if isinstance(value, six.binary_type):
        return value.decode(encoding, errors)
    raise TypeError("expected bytes or text, got %s" % type(value).__name__)


def to_bytes(value, encoding="utf-8", errors="strict"):
    """Return *value* as bytes (``str`` on Py2, ``bytes`` on Py3)."""
    if isinstance(value, six.binary_type):
        return value
    if isinstance(value, six.text_type):
        return value.encode(encoding, errors)
    raise TypeError("expected bytes or text, got %s" % type(value).__name__)
