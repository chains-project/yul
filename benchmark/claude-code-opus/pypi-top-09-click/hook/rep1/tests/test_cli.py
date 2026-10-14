import io
import json

import pytest

from mycli import __version__
from mycli.cli import main


def test_version(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert __version__ in capsys.readouterr().out


def test_missing_command_is_usage_error(capsys):
    with pytest.raises(SystemExit) as exc:
        main([])
    assert exc.value.code == 2
    assert "required" in capsys.readouterr().err


def test_greet_defaults(capsys):
    assert main(["greet", "Ada", "Linus"]) == 0
    assert capsys.readouterr().out == "Hello, Ada!\nHello, Linus!\n"


def test_greet_options(capsys):
    assert main(["greet", "-g", "Hi", "-n", "2", "--style", "shout", "Ada"]) == 0
    assert capsys.readouterr().out == "HI, ADA!\nHI, ADA!\n"


def test_greet_rejects_bad_choice(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["greet", "--style", "sing", "Ada"])
    assert exc.value.code == 2
    assert "invalid choice" in capsys.readouterr().err


def test_count_file(tmp_path, capsys):
    f = tmp_path / "a.txt"
    f.write_text("one two\nthree\n")
    assert main(["count", str(f)]) == 0
    assert capsys.readouterr().out.split() == ["2", "3", "14", str(f)]


def test_count_stdin_json(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", io.StringIO("a b c\n"))
    assert main(["count", "--words", "--json"]) == 0
    assert json.loads(capsys.readouterr().out) == [{"file": "-", "words": 3}]


def test_count_missing_file(tmp_path, capsys):
    assert main(["count", str(tmp_path / "nope.txt")]) == 1
    assert "no such file" in capsys.readouterr().err
