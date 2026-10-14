import json

import pytest

from mycli import __version__
from mycli.cli import main


@pytest.fixture
def cfg(tmp_path):
    return tmp_path / "config.json"


def run(capsys, *argv):
    code = main(list(argv))
    out, err = capsys.readouterr()
    return code, out, err


def test_version(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert __version__ in capsys.readouterr().out


def test_no_command_is_usage_error(capsys):
    with pytest.raises(SystemExit) as exc:
        main([])
    assert exc.value.code == 2
    assert "required" in capsys.readouterr().err


def test_greet(capsys):
    assert run(capsys, "greet", "Ada") == (0, "Hello, Ada!\n", "")


def test_greet_options(capsys):
    code, out, _ = run(capsys, "greet", "Ada", "-g", "Hi", "--times", "2", "--shout")
    assert code == 0
    assert out == "HI, ADA!\nHI, ADA!\n"


def test_greet_rejects_nonpositive_times(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["greet", "Ada", "--times", "0"])
    assert exc.value.code == 2
    assert "must be >= 1" in capsys.readouterr().err


def test_count_files(capsys, tmp_path):
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    a.write_text("one two\nthree\n")
    b.write_text("four\n")
    code, out, _ = run(capsys, "count", "-lw", str(a), str(b))
    assert code == 0
    rows = [line.split() for line in out.splitlines()]
    assert rows == [["2", "3", str(a)], ["1", "1", str(b)], ["3", "4", "total"]]


def test_count_stdin(capsys, monkeypatch):
    import io
    import sys

    monkeypatch.setattr(sys, "stdin", io.StringIO("hello world\n"))
    code, out, _ = run(capsys, "count", "-c")
    assert code == 0
    assert out.split()[0] == "12"


def test_config_roundtrip(capsys, cfg):
    assert run(capsys, "--config", str(cfg), "config", "set", "color", "blue")[0] == 0
    assert json.loads(cfg.read_text()) == {"color": "blue"}
    assert run(capsys, "--config", str(cfg), "config", "get", "color") == (0, "blue\n", "")
    assert run(capsys, "--config", str(cfg), "config", "list") == (0, "color=blue\n", "")
    assert run(capsys, "--config", str(cfg), "config", "unset", "color")[0] == 0
    assert json.loads(cfg.read_text()) == {}


def test_config_missing_key(capsys, cfg):
    code, out, err = run(capsys, "--config", str(cfg), "config", "get", "nope")
    assert code == 1
    assert out == ""
    assert "no such key: nope" in err


def test_config_invalid_file(capsys, cfg):
    cfg.write_text("not json")
    code, _, err = run(capsys, "--config", str(cfg), "config", "list")
    assert code == 1
    assert "invalid config file" in err


def test_count_missing_file(capsys, tmp_path):
    code, _, err = run(capsys, "count", str(tmp_path / "missing.txt"))
    assert code == 1
    assert "cannot read" in err
