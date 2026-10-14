# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from mylib import greet
from mylib._compat import binary_type, text_type, to_bytes, to_text


def test_greet_text():
    assert greet(u"wörld") == u"Hello, wörld!"


def test_greet_bytes():
    assert greet(u"wörld".encode("utf-8")) == u"Hello, wörld!"


def test_greet_returns_text():
    assert isinstance(greet(b"x"), text_type)


def test_round_trip():
    assert to_text(to_bytes(u"é")) == u"é"
    assert isinstance(to_bytes(u"é"), binary_type)
