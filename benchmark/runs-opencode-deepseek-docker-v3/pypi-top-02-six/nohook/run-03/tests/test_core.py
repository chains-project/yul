# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

from mylib import PY2, PY3, ensure_bytes, ensure_text, python_version
from mylib._compat import binary_type, text_type
from mylib.core import is_string


def test_python_flags_are_opposites():
    assert PY2 is not PY3
    assert PY2 or PY3


def test_python_version_matches_runtime():
    major, minor = python_version()
    assert (major, minor) == (2, 7) or major == 3
    assert major == 2 if PY2 else major == 3


def test_ensure_text_decodes_bytes():
    result = ensure_text(b"caf\xc3\xa9")
    assert isinstance(result, text_type)
    assert result == u"caf\xe9"


def test_ensure_text_is_idempotent_for_text():
    value = u"caf\xe9"
    assert ensure_text(value) is value


def test_ensure_bytes_encodes_text():
    result = ensure_bytes(u"caf\xe9")
    assert isinstance(result, binary_type)
    assert result == b"caf\xc3\xa9"


def test_ensure_bytes_is_idempotent_for_bytes():
    value = b"caf\xc3\xa9"
    assert ensure_bytes(value) is value


@pytest.mark.parametrize("bad", [None, 1, 1.5, object()])
def test_ensure_text_rejects_non_strings(bad):
    with pytest.raises(TypeError):
        ensure_text(bad)


@pytest.mark.parametrize("bad", [None, 1, 1.5, object()])
def test_ensure_bytes_rejects_non_strings(bad):
    with pytest.raises(TypeError):
        ensure_bytes(bad)


def test_is_string():
    assert is_string(u"text")
    assert is_string(b"bytes")
    assert not is_string(1)
    assert not is_string(None)
