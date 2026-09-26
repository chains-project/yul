from click.testing import CliRunner

from notemgr.cli import cli


def _run(runner, tmp_path, *args):
    return runner.invoke(cli, ["--store", str(tmp_path / "notes.json"), *args])


def test_add_and_list(tmp_path):
    runner = CliRunner()
    result = _run(runner, tmp_path, "add", "Buy milk", "--tag", "errand")
    assert result.exit_code == 0
    assert "Added note #1" in result.output

    result = _run(runner, tmp_path, "list")
    assert result.exit_code == 0
    assert "Buy milk" in result.output
    assert "errand" in result.output


def test_list_filters_by_tag(tmp_path):
    runner = CliRunner()
    _run(runner, tmp_path, "add", "Buy milk", "--tag", "errand")
    _run(runner, tmp_path, "add", "Finish report", "--tag", "work")

    result = _run(runner, tmp_path, "list", "--tag", "work")
    assert "Finish report" in result.output
    assert "Buy milk" not in result.output


def test_done_hides_note_by_default(tmp_path):
    runner = CliRunner()
    _run(runner, tmp_path, "add", "Buy milk")
    _run(runner, tmp_path, "done", "1")

    result = _run(runner, tmp_path, "list")
    assert "No notes found." in result.output

    result = _run(runner, tmp_path, "list", "--all")
    assert "Buy milk" in result.output


def test_remove_unknown_id_fails(tmp_path):
    runner = CliRunner()
    result = _run(runner, tmp_path, "remove", "99", "--yes")
    assert result.exit_code != 0
    assert "No note with id 99" in result.output
