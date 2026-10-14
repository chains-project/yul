# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

from mylib._compat import binary_type, ensure_binary, ensure_text, text_type


def test_ensure_text_roundtrip():
    assert ensure_text(b"caf\xc3\xa9") == "café"
    assert isinstance(ensure_text("café"), text_type)


def test_ensure_binary_roundtrip():
    assert ensure_binary("café") == b"caf\xc3\xa9"
    assert isinstance(ensure_binary(b"x"), binary_type)


@pytest.mark.parametrize("func", [ensure_text, ensure_binary])
def test_rejects_other_types(func):
    with pytest.raises(TypeError):
        func(42)
