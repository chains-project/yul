"""Tests for the ``mytool`` command-line interface."""

from __future__ import annotations

import io
import sys

import pytest

from mytool import __version__
from mytool.cli import main


def test_version(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(["--version"])
    assert excinfo.value.code == 0
    assert capsys.readouterr().out.strip() == f"mytool {__version__}"


def test_no_command_is_an_error() -> None:
    with pytest.raises(SystemExit) as excinfo:
        main([])
    assert excinfo.value.code == 2


def test_greet_defaults(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["greet"]) == 0
    assert capsys.readouterr().out == "Hello, world!\n"


def test_greet_options(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["greet", "Ada", "-g", "Hi", "-n", "2", "-u"]) == 0
    assert capsys.readouterr().out == "HI, ADA!\nHI, ADA!\n"


def test_greet_rejects_non_positive_count() -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(["greet", "-n", "0"])
    assert excinfo.value.code != 0


@pytest.mark.parametrize(
    ("argv", "expected"),
    [
        (["calc", "add", "2", "3", "4"], "9\n"),
        (["calc", "subtract", "10", "3"], "7\n"),
        (["calc", "multiply", "2", "2.5"], "5\n"),
        (["calc", "divide", "9", "2"], "4.5\n"),
    ],
)
def test_calc(argv: list[str], expected: str, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(argv) == 0
    assert capsys.readouterr().out == expected


def test_calc_division_by_zero(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["calc", "divide", "1", "0"]) == 1
    assert "division by zero" in capsys.readouterr().out


def test_wordcount_file(tmp_path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "sample.txt"
    path.write_text("hello world\nsecond line\n")
    assert main(["wordcount", str(path)]) == 0
    out = capsys.readouterr().out
    assert out.split()[0:3] == ["2", "4", "24"]
    assert out.strip().endswith(str(path))


def test_wordcount_stdin(monkeypatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("one two three\n"))
    assert main(["wordcount", "-w"]) == 0
    assert capsys.readouterr().out.strip() == "3"


def test_wordcount_totals(tmp_path, capsys: pytest.CaptureFixture[str]) -> None:
    first = tmp_path / "a.txt"
    second = tmp_path / "b.txt"
    first.write_text("a b c\n")
    second.write_text("d e\n")
    assert main(["wordcount", "-w", str(first), str(second)]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert lines[-1].strip() == "5 total"
