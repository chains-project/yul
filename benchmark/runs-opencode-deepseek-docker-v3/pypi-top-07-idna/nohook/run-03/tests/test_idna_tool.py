import pytest

from idna_tool import decode, encode
from idna_tool.cli import main

ENCODE_CASES = [
    ("example.com", "example.com"),
    ("bücher.de", "xn--bcher-kva.de"),
    ("例え.テスト", "xn--r8jz45g.xn--zckzah"),
]


@pytest.mark.parametrize(("unicode_name", "ascii_name"), ENCODE_CASES)
def test_encode(unicode_name, ascii_name):
    assert encode(unicode_name) == ascii_name


@pytest.mark.parametrize(("unicode_name", "ascii_name"), ENCODE_CASES)
def test_decode(unicode_name, ascii_name):
    assert decode(ascii_name) == unicode_name


def test_roundtrip():
    for unicode_name, _ in ENCODE_CASES:
        assert decode(encode(unicode_name)) == unicode_name


def test_cli_encode(capsys):
    assert main(["encode", "bücher.de"]) == 0
    assert capsys.readouterr().out.strip() == "xn--bcher-kva.de"


def test_cli_decode(capsys):
    assert main(["decode", "xn--bcher-kva.de"]) == 0
    assert capsys.readouterr().out.strip() == "bücher.de"


def test_cli_invalid_domain(capsys):
    assert main(["encode", "xn--"]) == 1
    assert capsys.readouterr().err.startswith("error:")
