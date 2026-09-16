"""CLI entry point with multiple subcommands."""

import click
from cli_tool.commands.build import build
from cli_tool.commands.deploy import deploy
from cli_tool.commands.info import info


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output.")
@click.option("--config", "-c", type=click.Path(exists=True), default=None, help="Path to config file.")
@click.version_option(version="0.1.0")
@click.pass_context
def cli(ctx, verbose, config):
    """CLI tool - a sample command-line application."""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["config"] = config


cli.add_command(build)
cli.add_command(deploy)
cli.add_command(info)


if __name__ == "__main__":
    cli()