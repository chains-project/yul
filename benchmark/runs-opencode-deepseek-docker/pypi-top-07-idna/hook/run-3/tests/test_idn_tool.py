import pytest

from idn_tool import IDNAError, decode, encode, to_ascii, to_unicode


def test_encode_basic():
    assert to_ascii("bücher.example") == "xn--bcher-kva.example"


def test_encode_returns_bytes():
    assert encode("bücher.example") == b"xn--bcher-kva.example"


def test_decode_basic():
    assert decode("xn--bcher-kva.example") == "bücher.example"


def test_decode_accepts_bytes():
    assert decode(b"xn--bcher-kva.example") == "bücher.example"


def test_roundtrip():
    domain = "münchen.de"
    assert to_unicode(to_ascii(domain)) == domain


def test_uts46_maps_uppercase():
    assert to_ascii("BÜCHER.example", uts46=True) == "xn--bcher-kva.example"


def test_invalid_domain_raises():
    with pytest.raises(IDNAError):
        to_ascii("xn--invalid-.example")
