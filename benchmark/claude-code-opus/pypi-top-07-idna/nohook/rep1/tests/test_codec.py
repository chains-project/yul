import idna
import pytest

from idna_tool import decode, encode
from idna_tool.cli import main


@pytest.mark.parametrize(
    "unicode_name, ascii_name",
    [
        ("example.com", "example.com"),
        ("bücher.de", "xn--bcher-kva.de"),
        ("münchen.de", "xn--mnchen-3ya.de"),
        ("例え.テスト", "xn--r8jz45g.xn--zckzah"),
    ],
)
def test_round_trip(unicode_name, ascii_name):
    assert encode(unicode_name) == ascii_name
    assert decode(ascii_name) == unicode_name


def test_uts46_case_folding():
    assert encode("Bücher.DE") == "xn--bcher-kva.de"


def test_idna2008_keeps_eszett():
    # IDNA 2003 (stdlib codec) maps ß -> ss; IDNA 2008 preserves it.
    assert encode("faß.de") == "xn--fa-hia.de"


def test_invalid_label_rejected():
    with pytest.raises(idna.IDNAError):
        encode("-bad-.com")


def test_cli(capsys):
    assert main(["encode", "bücher.de"]) == 0
    assert capsys.readouterr().out.strip() == "xn--bcher-kva.de"
    assert main(["decode", "xn--bcher-kva.de"]) == 0
    assert capsys.readouterr().out.strip() == "bücher.de"
    assert main(["encode", "--", "-bad-.com"]) == 1
