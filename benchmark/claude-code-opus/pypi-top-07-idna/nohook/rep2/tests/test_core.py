import pytest

from idnconv import IDNAError, decode, encode
from idnconv.cli import main


@pytest.mark.parametrize(
    ("unicode", "ascii_"),
    [
        ("bücher.de", "xn--bcher-kva.de"),
        ("münchen.example", "xn--mnchen-3ya.example"),
        ("例え.テスト", "xn--r8jz45g.xn--zckzah"),
        ("example.com", "example.com"),
    ],
)
def test_round_trip(unicode, ascii_):
    assert encode(unicode) == ascii_
    assert decode(ascii_) == unicode


def test_sharp_s_is_preserved_per_idna_2008():
    # IDNA 2003 (stdlib codec) would map this to "strasse.de".
    assert encode("straße.de") == "xn--strae-oqa.de"


def test_uts46_case_folds_by_default():
    assert encode("Bücher.DE") == "xn--bcher-kva.de"


def test_strict_mode_rejects_uppercase():
    with pytest.raises(IDNAError):
        encode("Bücher.de", uts46=False)


@pytest.mark.parametrize("bad", ["xn--a.com", "-leading.com", "a" * 64 + ".com"])
def test_invalid_names_raise(bad):
    with pytest.raises(IDNAError):
        decode(bad) if bad.startswith("xn--") else encode(bad)


def test_cli(capsys):
    assert main(["encode", "bücher.de", "bad_label.com"]) == 1
    out, err = capsys.readouterr()
    assert out == "xn--bcher-kva.de\n"
    assert "bad_label.com" in err

    assert main(["decode", "xn--bcher-kva.de"]) == 0
    assert capsys.readouterr().out == "bücher.de\n"
