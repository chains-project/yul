from click.testing import CliRunner

from mycli.cli import cli


def test_greet():
    runner = CliRunner()
    result = runner.invoke(cli, ["greet", "World"])
    assert result.exit_code == 0
    assert "Hello, World!" in result.output


def test_greet_count():
    runner = CliRunner()
    result = runner.invoke(cli, ["greet", "World", "--count", "3"])
    assert result.exit_code == 0
    assert result.output.count("Hello, World!") == 3


def test_config_set():
    runner = CliRunner()
    result = runner.invoke(cli, ["config", "set", "key", "value"])
    assert result.exit_code == 0
    assert "Set key = value" in result.output


def test_version():
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
