"""Tests for the greet subcommand."""

from click.testing import CliRunner

from cli_tool.cli import cli


def test_greet_basic():
    """Test basic greeting."""
    runner = CliRunner()
    result = runner.invoke(cli, ["greet", "Alice"])
    assert result.exit_code == 0
    assert "Hello Alice" in result.output


def test_greet_with_title():
    """Test greeting with title."""
    runner = CliRunner()
    result = runner.invoke(cli, ["greet", "Alice", "--title", "Dr."])
    assert result.exit_code == 0
    assert "Hello Dr. Alice" in result.output


def test_greet_count():
    """Test greeting with count."""
    runner = CliRunner()
    result = runner.invoke(cli, ["greet", "Alice", "--count", "3"])
    assert result.exit_code == 0
    assert "Greeting #1:" in result.output
    assert "Greeting #2:" in result.output
    assert "Greeting #3:" in result.output


def test_greet_json_format():
    """Test greeting with JSON output."""
    runner = CliRunner()
    result = runner.invoke(cli, ["greet", "Alice", "--format", "json"])
    assert result.exit_code == 0
    assert '"greeting"' in result.output


def test_greet_uppercase():
    """Test greeting with uppercase."""
    runner = CliRunner()
    result = runner.invoke(cli, ["greet", "alice", "--uppercase"])
    assert result.exit_code == 0
    assert "HELLO ALICE" in result.output


def test_greet_invalid_title():
    """Test greeting with invalid title raises error."""
    runner = CliRunner()
    result = runner.invoke(cli, ["greet", "Alice", "--title", "Invalid"])
    assert result.exit_code != 0


def test_version():
    """Test version output."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_help():
    """Test help output."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "cli-tool" in result.output
    assert "greet" in result.output
    assert "process" in result.output
    assert "generate" in result.output