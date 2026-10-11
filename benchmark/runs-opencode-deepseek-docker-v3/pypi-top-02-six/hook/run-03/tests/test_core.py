# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

import mylib
from mylib import _compat
from mylib.core import slugify


def test_slugify_basic():
    assert slugify("Hello, World!") == "hello-world"


def test_slugify_strips_edges():
    assert slugify("  --Spam & Eggs--  ") == "spam-eggs"


def test_slugify_accepts_non_strings():
    assert slugify(12345) == "12345"


def test_version_exposed():
    assert isinstance(mylib.__version__, _compat.string_types)


def test_to_text_roundtrip():
    assert _compat.to_text(b"caf\xc3\xa9") == "café"
    assert _compat.to_bytes("café") == b"caf\xc3\xa9"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
