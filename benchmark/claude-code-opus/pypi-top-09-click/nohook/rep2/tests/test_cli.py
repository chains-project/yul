import json

import pytest

from todo_cli.cli import build_parser, main


@pytest.fixture
def store(tmp_path, monkeypatch):
    path = tmp_path / "todo.json"
    monkeypatch.setenv("TODO_FILE", str(path))
    return path


def run(*argv):
    return main(list(argv))


def test_add_and_list(store, capsys):
    assert run("add", "buy", "milk", "-p", "high", "-t", "shop", "-t", "home") == 0
    assert "Added #1: buy milk" in capsys.readouterr().out

    data = json.loads(store.read_text())
    assert data[0]["text"] == "buy milk"
    assert data[0]["priority"] == "high"
    assert data[0]["tags"] == ["shop", "home"]

    run("list")
    out = capsys.readouterr().out
    assert "#1" in out and "buy milk (high)" in out and "[shop, home]" in out


def test_done_hides_from_default_list(store, capsys):
    run("add", "a")
    run("add", "b")
    run("done", "1")
    capsys.readouterr()

    run("list")
    out = capsys.readouterr().out
    assert "#1" not in out and "#2" in out

    run("ls", "--all")
    out = capsys.readouterr().out
    assert "[x] #1" in out


def test_done_undo(store, capsys):
    run("add", "a")
    run("done", "1")
    run("done", "1", "--undo")
    assert json.loads(store.read_text())[0]["done"] is False


def test_list_filters_and_json(store, capsys):
    run("add", "a", "-t", "work")
    run("add", "b", "-p", "high")
    run("add", "c", "-t", "work", "-p", "low")
    capsys.readouterr()

    run("list", "--tag", "work", "--format", "json")
    assert [i["text"] for i in json.loads(capsys.readouterr().out)] == ["a", "c"]

    run("list", "--sort", "priority", "--format", "json")
    assert [i["text"] for i in json.loads(capsys.readouterr().out)] == ["b", "a", "c"]


def test_remove_and_clear(store, capsys):
    for t in "abc":
        run("add", t)
    assert run("rm", "2", "-y") == 0
    run("done", "1")
    run("clear", "--dry-run")
    assert "Would remove 1" in capsys.readouterr().out
    assert len(json.loads(store.read_text())) == 2
    run("clear")
    assert [i["text"] for i in json.loads(store.read_text())] == ["c"]


def test_unknown_id_is_error(store, capsys):
    assert run("done", "42") == 1
    assert "no todo with id #42" in capsys.readouterr().err


def test_quiet_and_file_option_before_or_after_subcommand(tmp_path, capsys):
    path = tmp_path / "other.json"
    assert run("-q", "--file", str(path), "add", "x") == 0
    assert run("add", "y", "-q", "-f", str(path)) == 0
    assert capsys.readouterr().out == ""
    assert len(json.loads(path.read_text())) == 2


def test_corrupt_store_reports_error(store, capsys):
    store.write_text("{not json")
    assert run("list") == 1
    assert "could not read store" in capsys.readouterr().err


@pytest.mark.parametrize(
    "argv",
    [
        [],  # subcommand required
        ["bogus"],
        ["add"],  # text required
        ["add", "x", "-p", "urgent"],  # invalid choice
        ["done", "0"],  # ids must be positive
        ["done", "abc"],
    ],
)
def test_invalid_arguments_exit_2(argv, store):
    with pytest.raises(SystemExit) as exc:
        build_parser().parse_args(argv)
    assert exc.value.code == 2


def test_version(capsys):
    with pytest.raises(SystemExit) as exc:
        run("--version")
    assert exc.value.code == 0
    assert "todo 0.1.0" in capsys.readouterr().out
