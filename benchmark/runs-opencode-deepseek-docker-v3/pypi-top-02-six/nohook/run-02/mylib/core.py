"""Core library functionality.

The code in this module intentionally avoids version-specific syntax and
builtins; anything that differs between Python 2 and 3 lives in
:mod:`mylib._compat`.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

from ._compat import iteritems, string_types

__all__ = ["greet", "merge"]


def greet(name):
    """Return a friendly greeting for ``name``.

    :param name: the name to greet.
    :type name: ``str`` or ``unicode``
    :returns: the greeting.
    :rtype: ``unicode`` on Python 2, ``str`` on Python 3.
    """
    if not isinstance(name, string_types):
        raise TypeError("name must be a string, got {0!r}".format(type(name)))
    return "Hello, {0}!".format(name)


def merge(*mappings):
    """Merge any number of mappings into a single dictionary.

    Later mappings win over earlier ones when keys collide.
    """
    result = {}
    for mapping in mappings:
        for key, value in iteritems(mapping):
            result[key] = value
    return result
