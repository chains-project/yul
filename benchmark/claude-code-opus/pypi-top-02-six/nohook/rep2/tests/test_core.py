# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

from mylib import greet
from mylib._compat import ensure_binary, ensure_text, text_type


def test_greet_text():
    assert greet("wörld") == "Hello, wörld!"


def test_greet_bytes():
    assert greet("wörld".encode("utf-8")) == "Hello, wörld!"


def test_greet_returns_text():
    assert isinstance(greet("x"), text_type)


def test_ensure_roundtrip():
    assert ensure_text(ensure_binary("ünïcode")) == "ünïcode"


def test_ensure_text_rejects_other_types():
    with pytest.raises(TypeError):
        ensure_text(42)
