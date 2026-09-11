import six

from compatlib import to_text


def test_to_text_from_bytes():
    assert to_text(b"hello") == u"hello"


def test_to_text_from_text():
    assert to_text(u"hello") == u"hello"


def test_to_text_from_int():
    assert to_text(1) == six.text_type(1)
