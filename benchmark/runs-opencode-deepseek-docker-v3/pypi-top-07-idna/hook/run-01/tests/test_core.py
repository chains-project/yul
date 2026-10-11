import pytest

from idn_tool import IDNError, decode, encode, is_idn


@pytest.mark.parametrize(
    ("unicode", "ascii"),
    [
        ("münchen.de", "xn--mnchen-3ya.de"),
        ("例え.テスト", "xn--r8jz45g.xn--zckzah"),
        ("日本語.jp", "xn--wgv71a119e.jp"),
        ("example.com", "example.com"),
    ],
)
def test_encode(unicode: str, ascii: str) -> None:
    assert encode(unicode) == ascii


@pytest.mark.parametrize(
    ("unicode", "ascii"),
    [
        ("münchen.de", "xn--mnchen-3ya.de"),
        ("例え.テスト", "xn--r8jz45g.xn--zckzah"),
    ],
)
def test_decode(unicode: str, ascii: str) -> None:
    assert decode(ascii) == unicode


def test_round_trip() -> None:
    domain = "例え.テスト"
    assert decode(encode(domain)) == domain


def test_encode_trailing_dot() -> None:
    assert encode("münchen.de.") == "xn--mnchen-3ya.de."


def test_uts46_handles_case() -> None:
    with pytest.raises(IDNError):
        encode("Bücher.example")
    assert encode("Bücher.example", uts46=True) == "xn--bcher-kva.example"


def test_decode_accepts_bytes() -> None:
    assert decode(b"xn--mnchen-3ya.de") == "münchen.de"


def test_std3_rules_reject_underscore() -> None:
    with pytest.raises(IDNError):
        encode("_dmarc.example.com", std3_rules=True)


@pytest.mark.parametrize(
    "domain",
    ["xn--invalid-.com", "a..b", "-leading.example.com"],
)
def test_invalid_domains_raise(domain: str) -> None:
    with pytest.raises(IDNError):
        encode(domain)


def test_is_idn() -> None:
    assert is_idn("münchen.de")
    assert not is_idn("example.com")
