"""Example implementation shared by both Python majors."""
from __future__ import absolute_import, division, print_function, unicode_literals

import io

from ._compat import to_text


def greet(name):
    """Return ``"Hello, <name>!"`` as a text string.

    *name* may be either bytes or text; it is normalised with
    :func:`compatlib._compat.to_text`.
    """
    return "Hello, {0}!".format(to_text(name))


def read_text(path, encoding="utf-8"):
    """Read *path* and return its contents as text.

    Uses :func:`io.open` so that an explicit *encoding* is honoured on
    Python 2 as well as Python 3.
    """
    with io.open(path, "r", encoding=encoding) as handle:
        return handle.read()


def write_text(path, text, encoding="utf-8"):
    """Write *text* to *path* using an explicit *encoding*."""
    with io.open(path, "w", encoding=encoding) as handle:
        handle.write(to_text(text))
