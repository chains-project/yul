import pytest

from idna_tool import IDNAError, decode, encode
from idna_tool.cli import main


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


def test_eszett_is_preserved_under_idna2008():
    # IDNA 2003 (and Python's built-in codec) would map this to "fass.de".
    assert encode("faß.de") == "xn--fa-hia.de"


def test_uts46_case_folds():
    assert encode("Bücher.DE") == "xn--bcher-kva.de"


def test_strict_rejects_uppercase():
    with pytest.raises(IDNAError):
        encode("Bücher.de", uts46=False)


def test_invalid_label_rejected():
    with pytest.raises(IDNAError):
        encode("a" * 64 + ".com")


def test_cli(capsys):
    assert main(["encode", "bücher.de"]) == 0
    assert capsys.readouterr().out.strip() == "xn--bcher-kva.de"
    assert main(["decode", "xn--bcher-kva.de"]) == 0
    assert capsys.readouterr().out.strip() == "bücher.de"


def test_cli_error_exit_code(capsys):
    assert main(["encode", "a" * 64 + ".com"]) == 1
    assert "error" in capsys.readouterr().err
