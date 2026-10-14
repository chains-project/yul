# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import mylib
from mylib._compat import binary_type, text_type


def test_version():
    assert isinstance(mylib.__version__, text_type)


def test_to_text_from_bytes():
    result = mylib.to_text(b"caf\xc3\xa9")
    assert isinstance(result, text_type)
    assert result == "café"


def test_to_text_passthrough():
    assert mylib.to_text("café") == "café"


def test_to_text_from_int():
    assert mylib.to_text(42) == "42"


def test_to_bytes_from_text():
    result = mylib.to_bytes("café")
    assert isinstance(result, binary_type)
    assert result == b"caf\xc3\xa9"


def test_to_bytes_passthrough():
    assert mylib.to_bytes(b"\x00\xff") == b"\x00\xff"


def test_true_division():
    # Guaranteed by `from __future__ import division` on Python 2.
    assert 1 / 2 == 0.5
