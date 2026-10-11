import pytest

from idn_tools import (
    IDNAError,
    decode_domain,
    decode_label,
    encode_domain,
    encode_label,
)


@pytest.mark.parametrize(
    ("unicode", "ascii_"),
    [
        ("münchen.de", "xn--mnchen-3ya.de"),
        ("Bücher.example", "xn--bcher-kva.example"),
        ("例え.テスト", "xn--r8jz45g.xn--zckzah"),
        ("παράδειγμα.δοκιμή", "xn--hxajbheg2az3al.xn--jxalpdlp"),
        ("already-ascii.com", "already-ascii.com"),
    ],
)
def test_encode_domain(unicode, ascii_):
    assert encode_domain(unicode) == ascii_


@pytest.mark.parametrize(
    ("unicode", "ascii_"),
    [
        ("münchen.de", "xn--mnchen-3ya.de"),
        ("例え.テスト", "xn--r8jz45g.xn--zckzah"),
        ("already-ascii.com", "already-ascii.com"),
    ],
)
def test_decode_domain(unicode, ascii_):
    assert decode_domain(ascii_) == unicode


def test_round_trip():
    domain = "bücher.例え.example"
    assert decode_domain(encode_domain(domain)) == domain


def test_uts46_case_folding_and_normalization():
    assert encode_domain("BÜCHER.de") == "xn--bcher-kva.de"


def test_idna2008_keeps_sharp_s():
    assert encode_domain("faß.de") == "xn--fa-hia.de"


def test_ascii_bytes_input():
    assert encode_domain(b"xn--mnchen-3ya.de") == "xn--mnchen-3ya.de"
    assert decode_domain(b"xn--mnchen-3ya.de") == "münchen.de"


def test_strict_mode_rejects_disallowed_chars():
    with pytest.raises(IDNAError):
        encode_domain("foo_bar.example", uts46=False)


def test_empty_domain_rejected():
    with pytest.raises(IDNAError):
        encode_domain("")


def test_invalid_type_rejected():
    with pytest.raises(TypeError):
        encode_domain(123)


def test_label_helpers():
    assert encode_label("münchen") == "xn--mnchen-3ya"
    assert decode_label("xn--mnchen-3ya") == "münchen"
