from __future__ import absolute_import, unicode_literals

import pytest

from mylib.compat import PY2, PY3, binary_type, text_type, to_bytes, to_text


def test_python_version_flags_are_consistent():
    assert PY2 != PY3


def test_to_bytes_from_text():
    result = to_bytes("héllo")
    assert isinstance(result, binary_type)
    assert result == "héllo".encode("utf-8")


def test_to_bytes_is_idempotent():
    value = b"already bytes"
    assert to_bytes(value) is value


def test_to_text_from_bytes():
    result = to_text(b"h\xc3\xa9llo")
    assert isinstance(result, text_type)
    assert result == "héllo"


def test_to_text_is_idempotent():
    value = "already text"
    assert to_text(value) is value


@pytest.mark.parametrize("value", [1, None, object()])
def test_to_bytes_rejects_non_strings(value):
    with pytest.raises(TypeError):
        to_bytes(value)


@pytest.mark.parametrize("value", [1, None, object()])
def test_to_text_rejects_non_strings(value):
    with pytest.raises(TypeError):
        to_text(value)
