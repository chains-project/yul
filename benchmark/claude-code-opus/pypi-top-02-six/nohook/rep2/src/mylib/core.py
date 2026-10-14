from __future__ import absolute_import, division, print_function, unicode_literals

from mylib._compat import ensure_text


def greet(name):
    """Return a greeting for ``name``, which may be text or UTF-8 bytes."""
    return "Hello, {0}!".format(ensure_text(name))
