import json

import pytest

from mycli import __version__
from mycli.cli import main


def test_version(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert __version__ in capsys.readouterr().out


def test_command_required(capsys):
    with pytest.raises(SystemExit) as exc:
        main([])
    assert exc.value.code == 2
    assert "required" in capsys.readouterr().err


def test_greet_default(capsys):
    assert main(["greet"]) == 0
    assert capsys.readouterr().out == "Hello, world!\n"


def test_greet_options(capsys):
    assert main(["greet", "Ada", "--shout", "-n", "2", "--greeting", "Hi"]) == 0
    assert capsys.readouterr().out == "HI, ADA!\nHI, ADA!\n"


@pytest.mark.parametrize("bad", ["0", "-3", "abc"])
def test_greet_rejects_bad_times(bad, capsys):
    with pytest.raises(SystemExit) as exc:
        main(["greet", "--times", bad])
    assert exc.value.code == 2
    assert "--times" in capsys.readouterr().err


def test_count_file(tmp_path, capsys):
    f = tmp_path / "a.txt"
    f.write_text("one two\nthree\n")
    assert main(["count", str(f)]) == 0
    assert capsys.readouterr().out.split() == ["2", "3", "14", str(f)]


def test_count_selected_fields_json(tmp_path, capsys):
    f = tmp_path / "a.txt"
    f.write_text("one two\nthree\n")
    assert main(["count", "-l", "-w", "--format", "json", str(f)]) == 0
    assert json.loads(capsys.readouterr().out) == [{"name": str(f), "lines": 2, "words": 3}]


def test_count_stdin(monkeypatch, capsys):
    import io

    monkeypatch.setattr("sys.stdin", io.StringIO("a b c\n"))
    assert main(["count", "-w"]) == 0
    assert capsys.readouterr().out.split() == ["3", "-"]


def test_count_missing_file(tmp_path, capsys):
    missing = tmp_path / "nope.txt"
    assert main(["count", str(missing)]) == 1
    assert "no such file" in capsys.readouterr().err
