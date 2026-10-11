import pytest

from idnatool.cli import main


def test_encode_argument(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["encode", "例え.テスト"]) == 0
    assert capsys.readouterr().out == "xn--r8jz45g.xn--zckzah\n"


def test_decode_argument(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["decode", "xn--r8jz45g.xn--zckzah"]) == 0
    assert capsys.readouterr().out == "例え.テスト\n"


def test_multiple_arguments(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["encode", "bücher.example", "mañana.com"]) == 0
    assert capsys.readouterr().out == "xn--bcher-kva.example\nxn--maana-pta.com\n"


def test_reads_from_stdin(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr("sys.stdin", iter(["例え.テスト\n", "\n", "bücher.example\n"]))
    assert main(["encode"]) == 0
    assert capsys.readouterr().out == "xn--r8jz45g.xn--zckzah\nxn--bcher-kva.example\n"


def test_invalid_input_sets_exit_status(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["encode", "exa mple.com"]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "exa mple.com" in captured.err
