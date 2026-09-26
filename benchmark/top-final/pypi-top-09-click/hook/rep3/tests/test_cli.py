from click.testing import CliRunner

from taskcli.cli import cli


def test_add_and_list(tmp_path):
    runner = CliRunner()
    store = tmp_path / "tasks.json"

    result = runner.invoke(cli, ["--store", str(store), "add", "Write docs", "-p", "high"])
    assert result.exit_code == 0
    assert "Added task #1" in result.output

    result = runner.invoke(cli, ["--store", str(store), "list"])
    assert result.exit_code == 0
    assert "Write docs" in result.output


def test_done_and_remove(tmp_path):
    runner = CliRunner()
    store = tmp_path / "tasks.json"

    runner.invoke(cli, ["--store", str(store), "add", "Ship it"])
    result = runner.invoke(cli, ["--store", str(store), "done", "1"])
    assert result.exit_code == 0

    result = runner.invoke(cli, ["--store", str(store), "list"])
    assert "Ship it" not in result.output

    result = runner.invoke(cli, ["--store", str(store), "list", "--all"])
    assert "Ship it" in result.output

    result = runner.invoke(cli, ["--store", str(store), "remove", "1", "--yes"])
    assert result.exit_code == 0
    assert "Removed task #1" in result.output


def test_done_unknown_task(tmp_path):
    runner = CliRunner()
    store = tmp_path / "tasks.json"
    result = runner.invoke(cli, ["--store", str(store), "done", "99"])
    assert result.exit_code != 0
    assert "No task with id 99" in result.output
