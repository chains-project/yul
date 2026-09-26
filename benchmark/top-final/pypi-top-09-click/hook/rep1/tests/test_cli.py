from click.testing import CliRunner

from tasker.cli import cli


def test_add_and_list(tmp_path):
    store_path = tmp_path / "tasks.json"
    runner = CliRunner()

    result = runner.invoke(cli, ["--store-path", str(store_path), "add", "write tests", "-p", "high"])
    assert result.exit_code == 0
    assert "Added task #1" in result.output

    result = runner.invoke(cli, ["--store-path", str(store_path), "list"])
    assert result.exit_code == 0
    assert "write tests" in result.output


def test_done_and_remove(tmp_path):
    store_path = tmp_path / "tasks.json"
    runner = CliRunner()

    runner.invoke(cli, ["--store-path", str(store_path), "add", "ship it"])

    result = runner.invoke(cli, ["--store-path", str(store_path), "done", "1"])
    assert result.exit_code == 0
    assert "marked as done" in result.output

    result = runner.invoke(cli, ["--store-path", str(store_path), "remove", "1", "--yes"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_unknown_task_errors(tmp_path):
    store_path = tmp_path / "tasks.json"
    runner = CliRunner()

    result = runner.invoke(cli, ["--store-path", str(store_path), "done", "99"])
    assert result.exit_code != 0
    assert "No task with id 99" in result.output
