import pytest

from idna_tool import IDNAError, decode, encode
from idna_tool.cli import main


def test_encode():
    assert encode("münchen.de") == "xn--mnchen-3ya.de"


def test_decode():
    assert decode("xn--mnchen-3ya.de") == "münchen.de"


def test_roundtrip():
    domain = "例え.テスト"
    assert decode(encode(domain)) == domain


def test_uts46_case_folding():
    assert encode("MÜNCHEN.de") == "xn--mnchen-3ya.de"


def test_strict_rejects_uppercase():
    with pytest.raises(IDNAError):
        encode("MÜNCHEN.de", uts46=False)


def test_idna2008_differs_from_2003():
    # IDNA 2003 (Python's built-in codec) maps ß to "ss"; IDNA 2008 keeps it.
    assert encode("faß.de") == "xn--fa-hia.de"


def test_invalid_label():
    with pytest.raises(IDNAError):
        encode("a" * 64 + ".com")


def test_cli(capsys):
    assert main(["encode", "münchen.de"]) == 0
    assert capsys.readouterr().out.strip() == "xn--mnchen-3ya.de"
    assert main(["decode", "xn--mnchen-3ya.de"]) == 0
    assert capsys.readouterr().out.strip() == "münchen.de"
