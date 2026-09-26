from __future__ import absolute_import, division, print_function

import pytest

from mylib import greet


def test_greet():
    assert greet("World") == "Hello, World!"


def test_greet_rejects_non_string():
    with pytest.raises(TypeError):
        greet(123)
