"""Tests for the clitool command-line interface."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from clitool.cli import main


def test_greet_default(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["greet"]) == 0
    assert capsys.readouterr().out == "Hello, world!\n"


def test_greet_options(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["greet", "Ada", "-g", "Hi", "-c", "2", "-u"]) == 0
    assert capsys.readouterr().out == "HI, ADA!\nHI, ADA!\n"


def test_calc_add(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["calc", "add", "1", "2", "3"]) == 0
    assert capsys.readouterr().out == "add(1.0, 2.0, 3.0) = 6\n"


def test_calc_div_by_zero(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["calc", "div", "1", "0"]) == 1


def test_info_json(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["info", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert "clitool" in payload


def test_config_roundtrip(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    config = tmp_path / "config.json"

    assert main(["config", "--file", str(config), "set", "color", "blue"]) == 0
    assert main(["config", "--file", str(config), "get", "color"]) == 0
    assert capsys.readouterr().out == "blue\n"

    assert main(["config", "--file", str(config), "list"]) == 0
    assert capsys.readouterr().out == "color=blue\n"

    assert main(["config", "--file", str(config), "unset", "color"]) == 0
    assert main(["config", "--file", str(config), "get", "color"]) == 1


def test_version(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert capsys.readouterr().out.startswith("clitool ")
