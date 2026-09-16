"""Main CLI entry point with Click group and subcommands."""

import click

from cli_tool.commands.greet import greet
from cli_tool.commands.process import process
from cli_tool.commands.generate import generate


@click.group(invoke_without_command=True)
@click.version_option(version="0.1.0", prog_name="cli-tool")
@click.pass_context
def cli(ctx):
    """cli-tool - A multi-command CLI application.

    Use --help on any subcommand for detailed usage information.
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


cli.add_command(greet)
cli.add_command(process)
cli.add_command(generate)


def main():
    cli()


if __name__ == "__main__":
    main()