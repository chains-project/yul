import pytest

from idna_tool import decode, encode
from idna_tool.core import IDNAError


@pytest.mark.parametrize(
    ("unicode", "ascii"),
    [
        ("Bücher.example", "xn--bcher-kva.example"),
        ("例え.テスト", "xn--r8jz45g.xn--zckzah"),
        ("example.com", "example.com"),
        ("münchen.de", "xn--mnchen-3ya.de"),
    ],
)
def test_encode(unicode, ascii):
    assert encode(unicode) == ascii


@pytest.mark.parametrize(
    ("ascii", "unicode"),
    [
        ("xn--bcher-kva.example", "bücher.example"),
        ("xn--r8jz45g.xn--zckzah", "例え.テスト"),
        ("example.com", "example.com"),
    ],
)
def test_decode(ascii, unicode):
    assert decode(ascii) == unicode


def test_round_trip():
    original = "münchen.de"
    assert decode(encode(original)) == original


def test_encode_rejects_invalid():
    with pytest.raises(IDNAError):
        encode("exa mple.com")
