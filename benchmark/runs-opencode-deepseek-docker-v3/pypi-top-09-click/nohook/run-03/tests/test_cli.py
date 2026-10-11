from __future__ import annotations

import pytest

from mytool import __version__
from mytool.commands import config as config_cmd
from mytool.cli import main


def test_version(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert __version__ in capsys.readouterr().out


def test_no_command_prints_help(capsys):
    assert main([]) == 2
    assert "usage:" in capsys.readouterr().err


def test_greet_default(capsys):
    assert main(["greet"]) == 0
    assert capsys.readouterr().out == "Hello, world!\n"


def test_greet_options(capsys):
    assert main(["greet", "Ada", "--uppercase", "--repeat", "2"]) == 0
    assert capsys.readouterr().out == "HELLO, ADA!\nHELLO, ADA!\n"


def test_verbose_before_command(capsys):
    assert main(["--verbose", "greet", "Ada"]) == 0
    out = capsys.readouterr().out
    assert "greeting 'Ada'" in out
    assert out.endswith("Hello, Ada!\n")


def test_repeat_validation(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["greet", "--repeat", "0"])
    assert exc.value.code == 2


@pytest.fixture
def config_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("MYTOOL_CONFIG_DIR", str(tmp_path))
    return tmp_path


def test_config_set_get(config_dir, capsys):
    assert main(["config", "set", "color", "blue"]) == 0
    assert main(["config", "get", "color"]) == 0
    assert capsys.readouterr().out == "blue\n"


def test_config_list(config_dir, capsys):
    main(["config", "set", "b", "2"])
    main(["config", "set", "a", "1"])
    capsys.readouterr()
    assert main(["config", "list"]) == 0
    assert capsys.readouterr().out == "a=1\nb=2\n"


def test_config_get_missing(config_dir, capsys):
    assert main(["config", "get", "nope"]) == 1
    assert "no such key" in capsys.readouterr().out


def test_config_without_action_prints_help(config_dir, capsys):
    assert main(["config"]) == 2
    assert "usage:" in capsys.readouterr().out


def test_config_path_override(config_dir):
    assert config_cmd.config_path() == config_dir / "config.json"
