from click.testing import CliRunner

from taskcli.cli import cli


def invoke(runner, tasks_file, *args):
    return runner.invoke(cli, ["--tasks-file", str(tasks_file), *args])


def test_add_and_list(tmp_path):
    runner = CliRunner()
    tasks_file = tmp_path / "tasks.json"

    result = invoke(runner, tasks_file, "add", "Write report", "-p", "high", "-t", "work")
    assert result.exit_code == 0
    assert "Added task #1" in result.output

    result = invoke(runner, tasks_file, "list")
    assert result.exit_code == 0
    assert "#1 [high] Write report (work)" in result.output


def test_done_and_hidden_by_default(tmp_path):
    runner = CliRunner()
    tasks_file = tmp_path / "tasks.json"

    invoke(runner, tasks_file, "add", "Task one")
    result = invoke(runner, tasks_file, "done", "1")
    assert result.exit_code == 0
    assert "Completed task #1" in result.output

    result = invoke(runner, tasks_file, "list")
    assert "No tasks found." in result.output

    result = invoke(runner, tasks_file, "list", "--all")
    assert "[x] #1" in result.output


def test_done_missing_id_errors(tmp_path):
    runner = CliRunner()
    tasks_file = tmp_path / "tasks.json"

    result = invoke(runner, tasks_file, "done", "99")
    assert result.exit_code != 0
    assert "No task with id 99" in result.output


def test_remove_requires_confirmation(tmp_path):
    runner = CliRunner()
    tasks_file = tmp_path / "tasks.json"

    invoke(runner, tasks_file, "add", "Task one")
    result = invoke(runner, tasks_file, "remove", "1", "--yes")
    assert result.exit_code == 0
    assert "Removed 1 task(s)." in result.output

    result = invoke(runner, tasks_file, "list", "--all")
    assert "No tasks found." in result.output
