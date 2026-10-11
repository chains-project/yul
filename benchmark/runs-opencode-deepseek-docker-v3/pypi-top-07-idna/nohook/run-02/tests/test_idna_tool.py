import pytest

from idna_tool import IDNAError, decode, encode


def test_encode_unicode_domain():
    assert encode("例え.テスト") == "xn--r8jz45g.xn--zckzah"


def test_decode_ascii_domain():
    assert decode("xn--r8jz45g.xn--zckzah") == "例え.テスト"


def test_roundtrip():
    domain = "münchen.de"
    assert decode(encode(domain)) == domain


def test_uts46_lowercases_and_normalizes():
    assert encode("Bücher.example", uts46=True) == "xn--bcher-kva.example"


def test_invalid_domain_raises():
    with pytest.raises(IDNAError):
        encode("-leading-hyphen")
