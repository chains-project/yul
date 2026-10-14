# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import pytest
import six

from mylib import to_bytes, to_text


def test_to_text_decodes_bytes():
    result = to_text(b"caf\xc3\xa9")
    assert isinstance(result, six.text_type)
    assert result == u"café"


def test_to_text_passes_text_through():
    assert to_text(u"café") == u"café"


def test_to_bytes_encodes_text():
    result = to_bytes(u"café")
    assert isinstance(result, six.binary_type)
    assert result == b"caf\xc3\xa9"


def test_to_bytes_passes_bytes_through():
    assert to_bytes(b"abc") == b"abc"


@pytest.mark.parametrize("func", [to_text, to_bytes])
def test_rejects_non_string(func):
    with pytest.raises(TypeError):
        func(42)


def test_true_division():
    # Guards the ``from __future__ import division`` convention.
    assert 1 / 2 == 0.5
