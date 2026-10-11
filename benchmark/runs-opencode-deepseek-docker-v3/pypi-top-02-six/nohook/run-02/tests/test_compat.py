from __future__ import absolute_import, division, print_function, unicode_literals

from mylib._compat import (
    binary_type,
    integer_types,
    iterbytes,
    iteritems,
    string_types,
    text_type,
)


def test_string_types_include_text():
    assert isinstance("abc", string_types)


def test_text_type_holds_text():
    assert isinstance("abc", text_type)


def test_binary_type_is_bytes():
    assert isinstance(b"abc", binary_type)


def test_integer_types():
    assert isinstance(1, integer_types)


def test_iteritems_matches_dict_items():
    data = {"a": 1, "b": 2}
    assert dict(iteritems(data)) == data


def test_iterbytes_yields_ints():
    assert list(iterbytes(b"AB")) == [65, 66]
