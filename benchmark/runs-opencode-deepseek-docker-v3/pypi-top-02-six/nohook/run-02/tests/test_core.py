from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

from mylib import greet, merge
from mylib._compat import text_type


def test_greet_returns_text():
    result = greet("World")
    assert result == "Hello, World!"
    assert isinstance(result, text_type)


def test_greet_rejects_non_string():
    with pytest.raises(TypeError):
        greet(42)


def test_merge_combines_mappings():
    assert merge({"a": 1}, {"b": 2}) == {"a": 1, "b": 2}


def test_merge_later_wins():
    assert merge({"a": 1}, {"a": 2}) == {"a": 2}
