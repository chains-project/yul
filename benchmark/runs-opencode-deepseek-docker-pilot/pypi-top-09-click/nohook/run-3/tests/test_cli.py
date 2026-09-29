import json

import pytest

from taskbox import __version__
from taskbox.cli import main


@pytest.fixture
def store(tmp_path):
    return str(tmp_path / "tasks.json")


def test_version(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert __version__ in capsys.readouterr().out


def test_add_and_list(store, capsys):
    assert main(["--store", store, "add", "write docs"]) == 0
    capsys.readouterr()

    assert main(["--store", store, "list"]) == 0
    out = capsys.readouterr().out
    assert "write docs" in out
    assert "no tasks" not in out


def test_list_empty(store, capsys):
    assert main(["--store", store, "list"]) == 0
    assert "no tasks" in capsys.readouterr().out


def test_add_options_and_json(store, capsys):
    main(["--store", store, "add", "ship it", "-p", "high", "-t", "release", "-d", "2026-10-01"])
    capsys.readouterr()

    assert main(["--store", store, "list", "--json"]) == 0
    tasks = json.loads(capsys.readouterr().out)
    assert len(tasks) == 1
    assert tasks[0]["priority"] == "high"
    assert tasks[0]["tags"] == ["release"]
    assert tasks[0]["due"] == "2026-10-01"


def test_list_filters(store, capsys):
    main(["--store", store, "add", "low one", "-p", "low"])
    main(["--store", store, "add", "high one", "-p", "high", "-t", "urgent"])
    main(["--store", store, "done", "1"])
    capsys.readouterr()

    main(["--store", store, "list", "--status", "done", "--json"])
    done = json.loads(capsys.readouterr().out)
    assert [task["title"] for task in done] == ["low one"]

    main(["--store", store, "list", "--priority", "high", "--json"])
    high = json.loads(capsys.readouterr().out)
    assert [task["title"] for task in high] == ["high one"]

    main(["--store", store, "list", "--tag", "urgent", "--json"])
    tagged = json.loads(capsys.readouterr().out)
    assert [task["title"] for task in tagged] == ["high one"]


def test_done_and_remove(store, capsys):
    main(["--store", store, "add", "a"])
    main(["--store", store, "add", "b"])
    capsys.readouterr()

    assert main(["--store", store, "done", "1"]) == 0
    assert main(["--store", store, "remove", "2"]) == 0
    capsys.readouterr()

    main(["--store", store, "list", "--json"])
    tasks = json.loads(capsys.readouterr().out)
    assert len(tasks) == 1
    assert tasks[0]["done"] is True


def test_show(store, capsys):
    main(["--store", store, "add", "inspect me"])
    capsys.readouterr()
    assert main(["--store", store, "show", "1"]) == 0
    assert "inspect me" in capsys.readouterr().out


def test_missing_id_errors(store, capsys):
    main(["--store", store, "add", "only task"])
    capsys.readouterr()

    assert main(["--store", store, "done", "99"]) == 1
    err = capsys.readouterr().err
    assert "no such task" in err


def test_stats(store, capsys):
    main(["--store", store, "add", "a", "-p", "high"])
    main(["--store", store, "add", "b", "-p", "low"])
    main(["--store", store, "done", "2"])
    capsys.readouterr()

    assert main(["--store", store, "stats", "--json"]) == 0
    summary = json.loads(capsys.readouterr().out)
    assert summary["total"] == 2
    assert summary["done"] == 1
    assert summary["todo"] == 1
    assert summary["by_priority"]["high"] == 1


def test_alias_ls(store, capsys):
    main(["--store", store, "add", "aliased"])
    capsys.readouterr()
    assert main(["--store", store, "ls"]) == 0
    assert "aliased" in capsys.readouterr().out
