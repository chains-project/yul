from pathlib import Path

from click.testing import CliRunner

from taskcli.cli import cli


def test_add_and_list(tmp_path: Path) -> None:
    store = tmp_path / "tasks.json"
    runner = CliRunner()

    result = runner.invoke(cli, ["--store", str(store), "add", "Buy milk", "-p", "low"])
    assert result.exit_code == 0
    assert "Added task #1" in result.output

    result = runner.invoke(cli, ["--store", str(store), "list"])
    assert result.exit_code == 0
    assert "Buy milk" in result.output


def test_done_marks_task_complete(tmp_path: Path) -> None:
    store = tmp_path / "tasks.json"
    runner = CliRunner()

    runner.invoke(cli, ["--store", str(store), "add", "Ship it"])
    result = runner.invoke(cli, ["--store", str(store), "done", "1"])
    assert result.exit_code == 0

    result = runner.invoke(cli, ["--store", str(store), "list"])
    assert "Ship it" not in result.output

    result = runner.invoke(cli, ["--store", str(store), "list", "--all"])
    assert "Ship it" in result.output


def test_done_invalid_id(tmp_path: Path) -> None:
    store = tmp_path / "tasks.json"
    runner = CliRunner()

    result = runner.invoke(cli, ["--store", str(store), "done", "99"])
    assert result.exit_code != 0
    assert "No task #99" in result.output
