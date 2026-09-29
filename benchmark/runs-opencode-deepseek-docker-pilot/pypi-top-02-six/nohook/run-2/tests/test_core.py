from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

from mylib import greet, merge, normalize
from mylib._compat import PY2, text_type


def test_greet():
    assert greet("world") == "Hello, world!"


def test_greet_rejects_non_string():
    with pytest.raises(TypeError):
        greet(42)


def test_merge():
    assert merge({"a": 1}, {"b": 2}, {"a": 3}) == {"a": 3, "b": 2}


def test_normalize_unicode():
    assert normalize("  hello\tworld  ") == "hello world"


def test_normalize_bytes():
    assert normalize(b"  hello\tworld  ") == "hello world"


def test_text_type_is_unicode_everywhere():
    assert text_type("x") == "x"
    assert not isinstance(text_type("x"), bytes if not PY2 else str)
