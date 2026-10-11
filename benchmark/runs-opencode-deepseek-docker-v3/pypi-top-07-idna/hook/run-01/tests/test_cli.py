import pytest

from idn_tool.cli import main


def test_encode(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["encode", "münchen.de"]) == 0
    assert capsys.readouterr().out.strip() == "xn--mnchen-3ya.de"


def test_decode(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["decode", "xn--mnchen-3ya.de"]) == 0
    assert capsys.readouterr().out.strip() == "münchen.de"


def test_multiple_domains(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["encode", "münchen.de", "例え.テスト"]) == 0
    out = capsys.readouterr().out.splitlines()
    assert out == ["xn--mnchen-3ya.de", "xn--r8jz45g.xn--zckzah"]


def test_error_exit_code(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["decode", "xn--invalid-.com"]) == 1
    assert "error" in capsys.readouterr().err
