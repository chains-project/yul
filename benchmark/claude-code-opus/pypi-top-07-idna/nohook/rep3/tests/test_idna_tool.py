import pytest

from idna_tool import IDNAError, decode, encode
from idna_tool.cli import main


@pytest.mark.parametrize(
    "unicode_name, ascii_name",
    [
        ("bücher.example", "xn--bcher-kva.example"),
        ("münchen.de", "xn--mnchen-3ya.de"),
        ("例え.テスト", "xn--r8jz45g.xn--zckzah"),
        # IDNA 2008 keeps ß; IDNA 2003 (stdlib codec) would map it to "ss".
        ("faß.de", "xn--fa-hia.de"),
        ("example.com", "example.com"),
    ],
)
def test_round_trip(unicode_name, ascii_name):
    assert encode(unicode_name) == ascii_name
    assert decode(ascii_name) == unicode_name


def test_uts46_maps_uppercase():
    assert encode("BÜCHER.example") == "xn--bcher-kva.example"


def test_strict_rejects_uppercase():
    with pytest.raises(IDNAError):
        encode("BÜCHER.example", uts46=False)


def test_invalid_label_rejected():
    with pytest.raises(IDNAError):
        encode("a" * 64 + ".com")  # labels are limited to 63 octets


def test_cli(capsys):
    assert main(["encode", "bücher.example"]) == 0
    assert capsys.readouterr().out.strip() == "xn--bcher-kva.example"
    assert main(["decode", "xn--bcher-kva.example"]) == 0
    assert capsys.readouterr().out.strip() == "bücher.example"
