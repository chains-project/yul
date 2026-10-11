from __future__ import annotations

import pytest

from clitool.cli import main


def test_version(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert "clitool" in capsys.readouterr().out


def test_no_command_prints_help(capsys):
    assert main([]) == 2
    out = capsys.readouterr().out
    assert "usage:" in out
    assert "greet" in out and "calc" in out and "config" in out


def test_greet_default(capsys):
    assert main(["greet"]) == 0
    assert capsys.readouterr().out == "Hello, world!\n"


def test_greet_options(capsys):
    assert main(["greet", "Ada", "-u", "-c", "2"]) == 0
    assert capsys.readouterr().out == "HELLO, ADA!\nHELLO, ADA!\n"


def test_greet_bad_count(capsys):
    assert main(["greet", "-c", "0"]) == 2
    assert "positive integer" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("args", "expected"),
    [
        (["calc", "add", "1", "2", "3"], "6.000000"),
        (["calc", "sub", "10", "4"], "6.000000"),
        (["calc", "mul", "2", "3.5"], "7.000000"),
        (["calc", "add", "1", "2", "-p", "2"], "3.00"),
    ],
)
def test_calc(capsys, args, expected):
    assert main(args) == 0
    assert capsys.readouterr().out.strip() == expected


def test_calc_division_by_zero(capsys):
    assert main(["calc", "div", "1", "0"]) == 1
    assert "division by zero" in capsys.readouterr().out


def test_config_roundtrip(capsys, tmp_path):
    store = tmp_path / "cfg.json"
    assert main(["config", "-f", str(store), "-s", "color", "blue"]) == 0
    assert "color = blue" in capsys.readouterr().out

    assert main(["config", "-f", str(store), "-g", "color"]) == 0
    assert capsys.readouterr().out.strip() == "blue"

    assert main(["config", "-f", str(store), "--list"]) == 0
    assert "color = blue" in capsys.readouterr().out


def test_config_missing_key(capsys, tmp_path):
    store = tmp_path / "cfg.json"
    assert main(["config", "-f", str(store), "-g", "nope"]) == 1
    assert "no such key" in capsys.readouterr().out
