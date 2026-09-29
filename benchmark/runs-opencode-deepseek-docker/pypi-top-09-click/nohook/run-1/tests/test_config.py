import json

from mytool.cli import main


def test_set_then_get_roundtrip(tmp_path, capsys):
    cfg = tmp_path / "config.json"
    assert main(["config", "--file", str(cfg), "set", "greeting", "hi"]) == 0
    assert json.loads(cfg.read_text()) == {"greeting": "hi"}

    capsys.readouterr()
    assert main(["config", "--file", str(cfg), "get", "greeting"]) == 0
    assert capsys.readouterr().out == "hi\n"


def test_show_empty_config(tmp_path, capsys):
    cfg = tmp_path / "config.json"
    assert main(["config", "--file", str(cfg), "show"]) == 0
    assert capsys.readouterr().out == "{}\n"


def test_get_missing_key_returns_error(tmp_path, capsys):
    cfg = tmp_path / "config.json"
    assert main(["config", "--file", str(cfg), "get", "nope"]) == 1
    assert "no such key" in capsys.readouterr().err


def test_unset_removes_key(tmp_path):
    cfg = tmp_path / "config.json"
    main(["config", "--file", str(cfg), "set", "a", "1"])
    assert main(["config", "--file", str(cfg), "unset", "a"]) == 0
    assert json.loads(cfg.read_text()) == {}
