from click.testing import CliRunner

from taskcli.cli import cli


def test_add_and_list(tmp_path):
    store = tmp_path / "tasks.json"
    runner = CliRunner()

    result = runner.invoke(cli, ["-f", str(store), "add", "Buy milk", "-p", "high"])
    assert result.exit_code == 0
    assert "Added task #1" in result.output

    result = runner.invoke(cli, ["-f", str(store), "list"])
    assert result.exit_code == 0
    assert "Buy milk" in result.output


def test_done_and_remove(tmp_path):
    store = tmp_path / "tasks.json"
    runner = CliRunner()

    runner.invoke(cli, ["-f", str(store), "add", "Walk dog"])
    result = runner.invoke(cli, ["-f", str(store), "done", "1"])
    assert result.exit_code == 0

    result = runner.invoke(cli, ["-f", str(store), "remove", "1", "--yes"])
    assert result.exit_code == 0
    assert "Removed task #1" in result.output


def test_remove_missing_task(tmp_path):
    store = tmp_path / "tasks.json"
    runner = CliRunner()

    result = runner.invoke(cli, ["-f", str(store), "remove", "42", "--yes"])
    assert result.exit_code != 0
