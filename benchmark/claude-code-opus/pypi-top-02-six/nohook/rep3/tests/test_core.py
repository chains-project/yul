# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from mylib import greet
from mylib._compat import text_type, to_bytes, to_text


def test_greet_text():
    assert greet("wörld") == "Hello, wörld!"


def test_greet_bytes():
    result = greet("wörld".encode("utf-8"))
    assert isinstance(result, text_type)
    assert result == "Hello, wörld!"


def test_roundtrip():
    assert to_text(to_bytes("ünïcode")) == "ünïcode"
    assert isinstance(to_bytes("x"), bytes)
