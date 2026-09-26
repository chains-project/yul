from click.testing import CliRunner

from taskcli.cli import cli


def _store_args(tmp_path):
    return ["--store", str(tmp_path / "tasks.json")]


def test_add_and_list(tmp_path):
    runner = CliRunner()
    store = _store_args(tmp_path)

    result = runner.invoke(cli, [*store, "add", "Buy milk", "--priority", "high"])
    assert result.exit_code == 0
    assert "Added task #1" in result.output

    result = runner.invoke(cli, [*store, "list"])
    assert result.exit_code == 0
    assert "Buy milk" in result.output
    assert "(high)" in result.output


def test_done_hides_from_default_list(tmp_path):
    runner = CliRunner()
    store = _store_args(tmp_path)

    runner.invoke(cli, [*store, "add", "Water plants"])
    result = runner.invoke(cli, [*store, "done", "1"])
    assert result.exit_code == 0

    result = runner.invoke(cli, [*store, "list"])
    assert "Water plants" not in result.output

    result = runner.invoke(cli, [*store, "list", "--all"])
    assert "Water plants" in result.output


def test_remove_requires_confirmation(tmp_path):
    runner = CliRunner()
    store = _store_args(tmp_path)

    runner.invoke(cli, [*store, "add", "Old task"])
    result = runner.invoke(cli, [*store, "remove", "1"], input="y\n")
    assert result.exit_code == 0
    assert "Removed task #1" in result.output


def test_done_unknown_id_errors(tmp_path):
    runner = CliRunner()
    store = _store_args(tmp_path)

    result = runner.invoke(cli, [*store, "done", "99"])
    assert result.exit_code != 0
    assert "No task with id 99" in result.output
