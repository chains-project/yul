import pytest

from idn_toolkit import IDNError, decode, encode


@pytest.mark.parametrize(
    ("unicode_domain", "ascii_domain"),
    [
        ("example.com", "example.com"),
        ("münchen.de", "xn--mnchen-3ya.de"),
        ("bücher.example", "xn--bcher-kva.example"),
        ("例え.テスト", "xn--r8jz45g.xn--zckzah"),
        ("παράδειγμα.δοκιμή", "xn--hxajbheg2az3al.xn--jxalpdlp"),
    ],
)
def test_encode(unicode_domain, ascii_domain):
    assert encode(unicode_domain) == ascii_domain


@pytest.mark.parametrize(
    ("unicode_domain", "ascii_domain"),
    [
        ("example.com", "example.com"),
        ("münchen.de", "xn--mnchen-3ya.de"),
        ("例え.テスト", "xn--r8jz45g.xn--zckzah"),
    ],
)
def test_decode(unicode_domain, ascii_domain):
    assert decode(ascii_domain) == unicode_domain


def test_roundtrip():
    domain = "münchen.de"
    assert decode(encode(domain)) == domain


def test_encode_preserves_root_dot():
    assert encode("münchen.de.") == "xn--mnchen-3ya.de."


def test_mixed_labels_and_subdomain():
    assert encode("www.münchen.example.com") == "www.xn--mnchen-3ya.example.com"


def test_uts46_maps_uppercase_and_width():
    assert encode("BÜCHER.example", uts46=True) == "xn--bcher-kva.example"


def test_invalid_domain_raises():
    with pytest.raises(IDNError):
        encode("ab..cd")


def test_non_string_raises():
    with pytest.raises(TypeError):
        encode(123)
