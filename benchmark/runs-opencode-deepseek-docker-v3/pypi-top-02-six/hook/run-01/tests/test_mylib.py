from __future__ import absolute_import, division, print_function, unicode_literals

import mylib
from mylib._compat import PY2, to_bytes, to_unicode


def test_version():
    assert mylib.__version__


def test_py2_flag_is_bool():
    assert isinstance(PY2, bool)


def test_roundtrip_unicode():
    value = "h\u00e9llo"
    assert to_unicode(to_bytes(value)) == value


def test_to_bytes_from_text():
    assert to_bytes("abc") == b"abc"


def test_to_unicode_from_bytes():
    assert to_unicode(b"abc") == "abc"
