import pytest

from idnatool import IDNAError, decode, encode


@pytest.mark.parametrize(
    ("unicode", "ascii"),
    [
        ("example.com", "example.com"),
        ("münchen.de", "xn--mnchen-3ya.de"),
        ("日本語.jp", "xn--wgv71a119e.jp"),
        ("faß.de", "xn--fa-hia.de"),
        ("пример.рф", "xn--e1afmkfd.xn--p1ai"),
    ],
)
def test_encode(unicode: str, ascii: str) -> None:
    assert encode(unicode) == ascii


@pytest.mark.parametrize(
    ("ascii", "unicode"),
    [
        ("example.com", "example.com"),
        ("xn--mnchen-3ya.de", "münchen.de"),
        ("xn--wgv71a119e.jp", "日本語.jp"),
        ("xn--fa-hia.de", "faß.de"),
    ],
)
def test_decode(ascii: str, unicode: str) -> None:
    assert decode(ascii) == unicode


def test_round_trip_is_stable() -> None:
    domain = "日本語.jp"
    assert decode(encode(domain)) == domain


def test_decode_is_idempotent_on_ascii() -> None:
    assert decode("example.com") == "example.com"


def test_trailing_dot_is_preserved() -> None:
    assert encode("münchen.de.") == "xn--mnchen-3ya.de."


def test_encode_uts46_maps_uppercase() -> None:
    assert encode("MÜNCHEN.DE") == "xn--mnchen-3ya.de"


def test_invalid_label_raises() -> None:
    with pytest.raises(IDNAError):
        encode("a" * 64 + ".com")


def test_empty_label_raises() -> None:
    with pytest.raises(IDNAError):
        encode("example..com")


def test_disable_uts46_rejects_uppercase() -> None:
    with pytest.raises(IDNAError):
        encode("MÜNCHEN.DE", uts46=False)
