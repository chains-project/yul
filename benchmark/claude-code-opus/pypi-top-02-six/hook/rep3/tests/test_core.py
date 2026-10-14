# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from mylib import greet


def test_greet_text():
    assert greet("wörld") == "Hello, wörld!"


def test_greet_bytes():
    assert greet(b"world") == "Hello, world!"


def test_true_division():
    # Guards against `from __future__ import division` being dropped.
    assert 1 / 2 == 0.5
