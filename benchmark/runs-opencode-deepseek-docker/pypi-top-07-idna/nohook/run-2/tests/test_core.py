import pytest

from idna_toolkit import IDNAError, decode, decode_label, encode, encode_label, is_idn


@pytest.mark.parametrize(
    ("unicode_domain", "ascii_domain"),
    [
        ("例え.テスト", "xn--r8jz45g.xn--zckzah"),
        ("münchen.de", "xn--mnchen-3ya.de"),
        ("bücher.example", "xn--bcher-kva.example"),
        ("example.com", "example.com"),
    ],
)
def test_encode_known_vectors(unicode_domain, ascii_domain):
    assert encode(unicode_domain) == ascii_domain


@pytest.mark.parametrize(
    ("unicode_domain", "ascii_domain"),
    [
        ("例え.テスト", "xn--r8jz45g.xn--zckzah"),
        ("münchen.de", "xn--mnchen-3ya.de"),
        ("bücher.example", "xn--bcher-kva.example"),
        ("example.com", "example.com"),
    ],
)
def test_decode_known_vectors(unicode_domain, ascii_domain):
    assert decode(ascii_domain) == unicode_domain


@pytest.mark.parametrize("domain", ["例え.テスト", "münchen.de", "example.com"])
def test_round_trip(domain):
    assert decode(encode(domain)) == domain


def test_uts46_maps_case():
    assert encode("BÜCHER.example", uts46=True) == "xn--bcher-kva.example"


def test_uts46_rejected_without_flag():
    with pytest.raises(IDNAError):
        encode("BÜCHER.example")


def test_label_helpers():
    assert encode_label("例え") == "xn--r8jz45g"
    assert decode_label("xn--r8jz45g") == "例え"


@pytest.mark.parametrize(
    ("domain", "expected"),
    [
        ("xn--bcher-kva.example", True),
        ("bücher.example", True),
        ("example.com", False),
    ],
)
def test_is_idn(domain, expected):
    assert is_idn(domain) is expected


@pytest.mark.parametrize(
    "domain",
    [
        "例え..テスト",
        "xn--",
        "a" * 64 + ".com",
        "foo_bar.com",
        "",
    ],
)
def test_invalid_domains_raise(domain):
    with pytest.raises(IDNAError):
        encode(domain)


def test_non_string_raises():
    with pytest.raises(IDNAError):
        encode(b"example.com")  # type: ignore[arg-type]
    with pytest.raises(IDNAError):
        decode(b"example.com")  # type: ignore[arg-type]
