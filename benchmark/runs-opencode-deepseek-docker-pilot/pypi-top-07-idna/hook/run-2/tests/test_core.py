import pytest

from idn_toolkit import IDNAError, decode, encode


@pytest.mark.parametrize(
    ("unicode_domain", "ascii_domain"),
    [
        ("bücher.de", "xn--bcher-kva.de"),
        ("例え.テスト", "xn--r8jz45g.xn--zckzah"),
        ("münchen.example", "xn--mnchen-3ya.example"),
        ("example.com", "example.com"),
    ],
)
def test_encode(unicode_domain, ascii_domain):
    assert encode(unicode_domain) == ascii_domain


@pytest.mark.parametrize(
    ("ascii_domain", "unicode_domain"),
    [
        ("xn--bcher-kva.de", "bücher.de"),
        ("xn--r8jz45g.xn--zckzah", "例え.テスト"),
        ("example.com", "example.com"),
    ],
)
def test_decode(ascii_domain, unicode_domain):
    assert decode(ascii_domain) == unicode_domain


@pytest.mark.parametrize(
    "domain",
    ["bücher.de", "例え.テスト", "münchen.example", "sub.bücher.de"],
)
def test_roundtrip(domain):
    assert decode(encode(domain)) == domain


def test_decode_accepts_bytes():
    assert decode(b"xn--bcher-kva.de") == "bücher.de"


def test_uts46_folds_case():
    assert encode("BÜCHER.DE", uts46=True) == "xn--bcher-kva.de"


def test_uts46_folds_fullwidth():
    assert encode("ｅｘａｍｐｌｅ.com", uts46=True) == "example.com"


@pytest.mark.parametrize("domain", ["", "xn--", "a..b", "-leading.example"])
def test_invalid_domains_raise(domain):
    with pytest.raises(IDNAError):
        encode(domain)


def test_encode_rejects_non_str():
    with pytest.raises(TypeError):
        encode(b"bcher-kva.de")
