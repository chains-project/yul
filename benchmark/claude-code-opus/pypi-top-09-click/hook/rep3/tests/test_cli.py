import io
import json

import pytest

from mytool import __version__
from mytool.cli import main


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


def test_greet(capsys):
    assert main(["greet", "Ada", "Linus", "-g", "Hi", "--style", "shout"]) == 0
    assert capsys.readouterr().out == "HI, ADA!\nHI, LINUS!\n"


def test_greet_repeat(capsys):
    main(["greet", "Ada", "-n", "2"])
    assert capsys.readouterr().out == "Hello, Ada!\nHello, Ada!\n"


def test_greet_rejects_bad_choice(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["greet", "Ada", "--style", "loud"])
    assert exc.value.code == 2


def test_stats_file_json(tmp_path, capsys):
    f = tmp_path / "a.txt"
    f.write_text("one two\nthree\n")
    assert main(["stats", "--format", "json", str(f)]) == 0
    [result] = json.loads(capsys.readouterr().out)
    assert result == {"file": str(f), "lines": 2, "words": 3, "chars": 14}


def test_stats_stdin(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", io.StringIO("a b c\n"))
    assert main(["stats"]) == 0
    assert capsys.readouterr().out.split() == ["1", "3", "6", "-"]


def test_stats_missing_file(tmp_path, capsys):
    assert main(["stats", str(tmp_path / "nope.txt")]) == 1
    assert "cannot read" in capsys.readouterr().err


def test_config_roundtrip(tmp_path, capsys):
    cfg = ["config", "--file", str(tmp_path / "c.json")]
    assert main([*cfg, "set", "color", "blue"]) == 0
    assert main([*cfg, "set", "size", "3"]) == 0
    assert main([*cfg, "get", "color"]) == 0
    assert capsys.readouterr().out == "blue\n"

    assert main([*cfg, "list"]) == 0
    assert capsys.readouterr().out == "color=blue\nsize=3\n"

    assert main([*cfg, "unset", "color"]) == 0
    assert main([*cfg, "get", "color"]) == 1
    assert "key not found" in capsys.readouterr().err


def test_config_uses_xdg_path(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    main(["config", "set", "k", "v"])
    assert (tmp_path / "mytool" / "config.json").exists()
