import pytest

from idnatool import IDNAError, decode_domain, encode_domain


@pytest.mark.parametrize(
    ("unicode", "ascii"),
    [
        ("例え.テスト", "xn--r8jz45g.xn--zckzah"),
        ("bücher.example", "xn--bcher-kva.example"),
        ("münchen.de", "xn--mnchen-3ya.de"),
        ("mañana.com", "xn--maana-pta.com"),
        ("日本語.jp", "xn--wgv71a119e.jp"),
        ("faß.de", "xn--fa-hia.de"),
    ],
)
def test_encode_known_vectors(unicode: str, ascii: str) -> None:
    assert encode_domain(unicode) == ascii


@pytest.mark.parametrize(
    ("unicode", "ascii"),
    [
        ("例え.テスト", "xn--r8jz45g.xn--zckzah"),
        ("bücher.example", "xn--bcher-kva.example"),
    ],
)
def test_round_trip(unicode: str, ascii: str) -> None:
    assert decode_domain(ascii) == unicode
    assert encode_domain(decode_domain(ascii)) == ascii


def test_encode_is_lowercase() -> None:
    assert encode_domain("BÜCHER.example") == "xn--bcher-kva.example"


def test_encode_preserves_trailing_dot() -> None:
    assert encode_domain("例え.テスト.") == "xn--r8jz45g.xn--zckzah."
    assert decode_domain("xn--r8jz45g.xn--zckzah.") == "例え.テスト."


def test_alt_dot_separators() -> None:
    assert encode_domain("例え。テスト") == "xn--r8jz45g.xn--zckzah"


def test_empty_domain() -> None:
    assert encode_domain("") == ""
    assert decode_domain("") == ""


def test_root_domain() -> None:
    assert encode_domain(".") == "."
    assert decode_domain(".") == "."


def test_ascii_only_domain_unchanged() -> None:
    assert encode_domain("example.com") == "example.com"
    assert decode_domain("example.com") == "example.com"


def test_invalid_domain_raises() -> None:
    with pytest.raises(IDNAError):
        encode_domain("exa mple.com")


def test_invalid_ulabel_raises() -> None:
    with pytest.raises(IDNAError):
        decode_domain("xn--a.example")


def test_non_str_raises_type_error() -> None:
    with pytest.raises(TypeError):
        encode_domain(b"example.com")  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        decode_domain(b"example.com")  # type: ignore[arg-type]
