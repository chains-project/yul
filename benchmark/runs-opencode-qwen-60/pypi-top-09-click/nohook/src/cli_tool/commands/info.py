"""Info command subcommand."""

import click
import platform


@click.command()
@click.option("--all", "-a", is_flag=True, help="Show all available info.")
@click.option("--json", "-j", "as_json", is_flag=True, help="Output as JSON.")
@click.pass_context
def info(ctx, all, as_json):
    """Show system and tool information."""
    verbose = ctx.obj.get("verbose", False)
    click.echo(f"CLI tool version: 0.1.0")
    click.echo(f"Python: {platform.python_version()}")
    click.echo(f"Platform: {platform.platform()}")
    if all:
        click.echo(f"Config file: {ctx.obj.get('config', 'None')}")
        click.echo(f"Verbose: {verbose}")