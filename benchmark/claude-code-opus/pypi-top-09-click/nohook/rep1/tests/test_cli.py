import json

import pytest

from mycli import __version__
from mycli.cli import main


def test_version(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert __version__ in capsys.readouterr().out


def test_requires_subcommand(capsys):
    with pytest.raises(SystemExit) as exc:
        main([])
    assert exc.value.code == 2


def test_greet(capsys):
    assert main(["greet", "Ada", "Linus", "-g", "Hi", "-n", "2", "--shout"]) == 0
    assert capsys.readouterr().out == "HI, ADA, LINUS!\n" * 2


def test_greet_invalid_times(capsys):
    assert main(["greet", "Ada", "-n", "0"]) == 1
    assert "--times must be at least 1" in capsys.readouterr().err


def test_stats_text(tmp_path, capsys):
    p = tmp_path / "a.txt"
    p.write_text("one two\nthree\n")
    assert main(["stats", str(p)]) == 0
    assert capsys.readouterr().out == f"2\t3\t14\t{p}\n"


def test_stats_json_only(tmp_path, capsys):
    p = tmp_path / "a.txt"
    p.write_text("one two\nthree\n")
    assert main(["stats", str(p), "-f", "json", "--only", "words"]) == 0
    assert json.loads(capsys.readouterr().out) == [{"file": str(p), "words": 3}]


def test_stats_missing_file(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["stats", "does-not-exist.txt"])
    assert exc.value.code == 2
