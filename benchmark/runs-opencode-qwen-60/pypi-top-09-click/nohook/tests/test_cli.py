"""Tests for CLI commands."""

from click.testing import CliRunner
from cli_tool.cli import cli


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "CLI tool" in result.output
    assert "build" in result.output
    assert "deploy" in result.output
    assert "info" in result.output


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_build_command():
    runner = CliRunner()
    result = runner.invoke(cli, ["build", "release", "-o", "./out", "-j", "4", "-f", "-v"])
    assert result.exit_code == 0
    assert "target: release" in result.output
    assert "Output directory: ./out" in result.output
    assert "Parallel jobs: 4" in result.output
    assert "Force rebuild enabled." in result.output
    assert "Verbose mode on." in result.output


def test_build_default():
    runner = CliRunner()
    result = runner.invoke(cli, ["build"])
    assert result.exit_code == 0
    assert "target: release" in result.output


def test_deploy_command():
    runner = CliRunner()
    result = runner.invoke(cli, ["deploy", "production", "-r", "eu-west-1", "--dry-run", "-t", "v1"])
    assert result.exit_code == 0
    assert "Deploying to: production" in result.output
    assert "Region: eu-west-1" in result.output
    assert "Tag: v1" in result.output
    assert "Dry run - no changes applied." in result.output


def test_deploy_staging():
    runner = CliRunner()
    result = runner.invoke(cli, ["deploy", "staging"])
    assert result.exit_code == 0
    assert "Deploying to: staging" in result.output


def test_info_command():
    runner = CliRunner()
    result = runner.invoke(cli, ["info", "-a"])
    assert result.exit_code == 0
    assert "CLI tool version: 0.1.0" in result.output
    assert "Python:" in result.output
    assert "Platform:" in result.output


def test_subcommand_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["build", "--help"])
    assert result.exit_code == 0
    assert "Build the project" in result.output