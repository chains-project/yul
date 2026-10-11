"""Core, interpreter-agnostic functionality for :mod:`mylib`."""

from __future__ import absolute_import, division, print_function, unicode_literals

import re
import unicodedata

from ._compat import text_type

__all__ = ["chunked", "slugify", "items"]

_SLUG_RE = re.compile(r"[^\w\s-]", re.UNICODE)
_WHITESPACE_RE = re.compile(r"[-\s]+", re.UNICODE)


def slugify(value, allow_unicode=False):
    """Convert ``value`` to a URL-friendly slug.

    Unlike ``django.utils.text.slugify`` this helper never touches the active
    locale, so it behaves identically on Python 2 and Python 3.

    :param value: any object whose ``text_type`` representation is meaningful.
    :param allow_unicode: keep non-ASCII word characters.  When ``False``
        (the default) accented characters are transliterated to their ASCII
        equivalents (``é`` becomes ``e``).
    """
    value = text_type(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
        value = _SLUG_RE.sub("", value)
    else:
        value = unicodedata.normalize("NFKD", value)
        value = value.encode("ascii", "ignore").decode("ascii")
        value = _SLUG_RE.sub("", value)
    value = value.strip().lower()
    return _WHITESPACE_RE.sub("-", value)


def chunked(iterable, size):
    """Yield successive lists of at most ``size`` items from ``iterable``.

    The final chunk may be shorter than ``size``.  This is a generator so it
    works with arbitrary iterables, not just sequences, on both interpreters.
    """
    if size < 1:
        raise ValueError("size must be >= 1")
    chunk = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) == size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


def items(mapping):
    """Return an iterator over ``(key, value)`` pairs of ``mapping``.

    On Python 2 this avoids materialising the full list that
    ``dict.items()`` would create; on Python 3 it is simply
    ``mapping.items()``.
    """
    from ._compat import iteritems

    return iteritems(mapping)
