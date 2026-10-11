# -*- coding: utf-8 -*-
"""Tests for :mod:`mylib.core`."""
from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

from mylib import chunked, slugify
from mylib.core import items


def test_slugify_basic():
    assert slugify("Hello, World!") == "hello-world"


def test_slugify_collapses_separators():
    assert slugify("  Foo   --  Bar  ") == "foo-bar"


def test_slugify_drops_non_ascii_by_default():
    assert slugify("Héllo Wörld") == "hello-world"


def test_slugify_can_keep_unicode():
    assert slugify("Héllo Wörld", allow_unicode=True) == "héllo-wörld"


def test_slugify_accepts_non_string():
    assert slugify(12345) == "12345"


def test_chunked_even_split():
    assert list(chunked(range(6), 2)) == [[0, 1], [2, 3], [4, 5]]


def test_chunked_uneven_split():
    assert list(chunked(range(7), 3)) == [[0, 1, 2], [3, 4, 5], [6]]


def test_chunked_empty():
    assert list(chunked([], 3)) == []


def test_chunked_rejects_bad_size():
    with pytest.raises(ValueError):
        list(chunked([1, 2, 3], 0))


def test_items_iterates_pairs():
    assert sorted(items({"a": 1, "b": 2})) == [("a", 1), ("b", 2)]
