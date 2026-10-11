# -*- coding: utf-8 -*-
"""Tests for the Python 2/3 compatibility helpers."""
from __future__ import absolute_import, division, print_function, unicode_literals

import sys

from mylib._compat import (
    PY2,
    PY3,
    binary_type,
    to_bytes,
    to_native,
    to_text,
)


def test_py2_py3_flags_are_consistent():
    assert PY2 != PY3
    assert PY3 == (sys.version_info[0] == 3)


def test_to_bytes_from_text():
    assert to_bytes("café") == "café".encode("utf-8")


def test_to_bytes_is_idempotent():
    value = b"already bytes"
    assert to_bytes(value) is value


def test_to_text_from_bytes():
    assert to_text("café".encode("utf-8")) == "café"


def test_to_text_is_idempotent():
    value = "already text"
    assert to_text(value) is value


def test_to_native_matches_interpreter():
    native = to_native("café")
    if PY2:
        assert isinstance(native, binary_type)
    else:
        assert isinstance(native, str)
