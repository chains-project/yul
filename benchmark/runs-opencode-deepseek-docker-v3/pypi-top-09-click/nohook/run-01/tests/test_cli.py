"""End-to-end tests exercising the parser and command handlers."""

from __future__ import annotations

import json

import pytest

from clitool.cli import main


def test_no_command_prints_help(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([]) == 2
    assert "usage: clitool" in capsys.readouterr().err


def test_version(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(["--version"])
    assert excinfo.value.code == 0
    assert "clitool" in capsys.readouterr().out


def test_hello_defaults(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["hello"]) == 0
    assert capsys.readouterr().out == "Hello, world!\n"


def test_hello_options(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["hello", "Ada", "-g", "Hi", "-c", "2", "--shout"]) == 0
    assert capsys.readouterr().out == "HI, ADA!\nHI, ADA!\n"


@pytest.mark.parametrize("value", ["0", "-3", "nope"])
def test_hello_rejects_bad_count(value: str) -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(["hello", "-c", value])
    assert excinfo.value.code == 2


def test_tasks_lifecycle(tmp_path, capsys: pytest.CaptureFixture[str]) -> None:
    store = tmp_path / "tasks.json"

    assert main(["tasks", "-f", str(store), "add", "write tests", "-t", "dev"]) == 0
    add_out = capsys.readouterr().out
    task_id = add_out.split()[1].rstrip(":")

    assert main(["tasks", "-f", str(store), "list"]) == 0
    assert "write tests" in capsys.readouterr().out

    assert main(["tasks", "-f", str(store), "list", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload[0]["tags"] == ["dev"]

    assert main(["tasks", "-f", str(store), "done", task_id]) == 0
    capsys.readouterr()

    assert main(["tasks", "-f", str(store), "list"]) == 0
    assert "no tasks" in capsys.readouterr().out

    assert main(["tasks", "-f", str(store), "list", "--all"]) == 0
    assert "[x]" in capsys.readouterr().out

    assert main(["tasks", "-f", str(store), "remove", task_id]) == 0
    assert "removed 1 task(s)" in capsys.readouterr().out


def test_tasks_unknown_id(tmp_path, capsys: pytest.CaptureFixture[str]) -> None:
    store = tmp_path / "tasks.json"
    assert main(["tasks", "-f", str(store), "done", "deadbeef"]) == 1
    assert "unknown task id" in capsys.readouterr().err


def test_config_roundtrip(tmp_path, capsys: pytest.CaptureFixture[str]) -> None:
    config = tmp_path / "config.json"

    assert main(["--config", str(config), "config", "set", "user.name", "Ada"]) == 0
    assert main(["--config", str(config), "config", "set", "user.age", "36"]) == 0
    capsys.readouterr()

    assert main(["--config", str(config), "config", "get", "user.name"]) == 0
    assert capsys.readouterr().out == "Ada\n"

    assert main(["--config", str(config), "config", "get", "user.age"]) == 0
    assert capsys.readouterr().out == "36\n"

    assert main(["--config", str(config), "config", "unset", "user.age"]) == 0
    capsys.readouterr()

    assert main(["--config", str(config), "config", "list"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data == {"user": {"name": "Ada"}}


def test_config_missing_key(tmp_path, capsys: pytest.CaptureFixture[str]) -> None:
    config = tmp_path / "config.json"
    assert main(["--config", str(config), "config", "get", "nope"]) == 1
    assert "no such config key" in capsys.readouterr().err
