# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

import mylib
from mylib import greet
from mylib._compat import string_types
from mylib.core import utf8_len


def test_version_is_exposed():
    assert mylib.__version__ == "0.1.0"


def test_greet_returns_text():
    result = greet("World")
    assert result == "Hello, World!"
    assert isinstance(result, string_types)


def test_greet_accepts_custom_greeting():
    assert greet("World", greeting="Hi") == "Hi, World!"


def test_greet_rejects_non_string():
    with pytest.raises(TypeError):
        greet(42)


def test_utf8_len_unicode_literal():
    assert utf8_len("café") == 5


def test_utf8_len_bytes():
    assert utf8_len("café".encode("utf-8")) == 5
