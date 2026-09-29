import pytest

from idnatool import IDNAError, Profile, decode, encode


def test_encode_unicode_to_alabel():
    assert encode("bücher.example") == "xn--bcher-kva.example"


def test_decode_alabel_to_unicode():
    assert decode("xn--bcher-kva.example") == "bücher.example"


def test_round_trip():
    domain = "例え.テスト"
    assert decode(encode(domain)) == domain


def test_ascii_passthrough():
    assert encode("example.com") == "example.com"


def test_idna2008_requires_normalized_input():
    with pytest.raises(IDNAError):
        encode("Bücher.example")
    with pytest.raises(IDNAError):
        encode("Bu\u0308cher.example")  # NFD: u + combining diaeresis


def test_uts46_maps_case_and_normalizes():
    assert encode("Bücher.example", profile=Profile.UTS46) == "xn--bcher-kva.example"
    assert encode("Bu\u0308cher.example", profile=Profile.UTS46) == "xn--bcher-kva.example"


def test_deviation_characters_kept():
    assert encode("faß.de") == "xn--fa-hia.de"
    assert decode("xn--fa-hia.de") == "faß.de"


def test_profile_accepts_plain_string():
    assert encode("Bücher.example", profile="uts46") == "xn--bcher-kva.example"


def test_invalid_domain_raises():
    with pytest.raises(IDNAError):
        encode("")
    with pytest.raises(IDNAError):
        encode("foo..bar")


def test_unknown_profile_raises():
    with pytest.raises(IDNAError):
        encode("example.com", profile="bogus")


def test_encode_rejects_bytes():
    with pytest.raises(IDNAError):
        encode(b"example.com")


def test_decode_accepts_bytes():
    assert decode(b"xn--bcher-kva.example") == "bücher.example"
