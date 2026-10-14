import pytest

from idna_tool import decode, encode, main


@pytest.mark.parametrize(
    ("unicode", "ascii"),
    [
        ("bücher.de", "xn--bcher-kva.de"),
        ("münchen.example", "xn--mnchen-3ya.example"),
        ("例え.テスト", "xn--r8jz45g.xn--zckzah"),
        ("example.com", "example.com"),
    ],
)
def test_round_trip(unicode, ascii):
    assert encode(unicode) == ascii
    assert decode(ascii) == unicode


def test_uts46_mapping_case_folds():
    assert encode("Bücher.DE") == "xn--bcher-kva.de"


def test_idna2008_differs_from_idna2003():
    # IDNA 2003 (Python's built-in codec) maps ß to "ss"; IDNA 2008 keeps it.
    assert encode("faß.de") == "xn--fa-hia.de"
    assert "faß.de".encode("idna") == b"fass.de"


def test_strict_rejects_uppercase():
    assert main(["encode", "--strict", "Bücher.de"]) == 1


def test_cli(capsys):
    assert main(["encode", "bücher.de"]) == 0
    assert capsys.readouterr().out == "xn--bcher-kva.de\n"
    assert main(["decode", "xn--bcher-kva.de"]) == 0
    assert capsys.readouterr().out == "bücher.de\n"
