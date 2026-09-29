from __future__ import absolute_import, unicode_literals

import pytest

from mylib import decode, encode, greet, iter_dict, loads
from mylib.compat import text_type


def test_greet_with_text():
    assert greet("World") == "Hello, World!"


def test_greet_with_bytes():
    assert greet(b"World") == "Hello, World!"


def test_greet_returns_text():
    assert isinstance(greet("World"), text_type)


def test_greet_rejects_non_strings():
    with pytest.raises(TypeError):
        greet(42)


@pytest.mark.parametrize("value", ["", "hello", "héllo", "a" * 512])
def test_encode_decode_roundtrip(value):
    assert decode(encode(value)) == value


def test_encode_matches_base64_module():
    import base64

    assert encode("payload") == base64.b64encode(b"payload").decode("ascii")


def test_decode_accepts_bytes():
    assert decode(b"cGF5bG9hZA==") == "payload"


def test_loads_from_bytes_and_text():
    assert loads(b'{"a": 1}') == {"a": 1}
    assert loads('{"a": 1}') == {"a": 1}


def test_iter_dict_yields_pairs():
    assert sorted(iter_dict({"b": 2, "a": 1})) == [("a", 1), ("b", 2)]
