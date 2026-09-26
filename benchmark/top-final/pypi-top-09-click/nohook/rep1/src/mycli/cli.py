import click

from mycli import __version__


@click.group()
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose output.")
@click.version_option(__version__, "--version")
@click.pass_context
def cli(ctx: click.Context, verbose: bool) -> None:
    """mycli - a sample command-line tool with subcommands."""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose


@cli.command()
@click.argument("name")
@click.option("-c", "--count", default=1, show_default=True, help="Number of greetings.")
@click.pass_context
def greet(ctx: click.Context, name: str, count: int) -> None:
    """Greet NAME."""
    for _ in range(count):
        if ctx.obj.get("verbose"):
            click.echo(f"[verbose] greeting {name}")
        click.echo(f"Hello, {name}!")


@cli.group()
def config() -> None:
    """Manage configuration values."""


@config.command("get")
@click.argument("key")
def config_get(key: str) -> None:
    """Get the value for KEY."""
    click.echo(f"{key} = <not set>")


@config.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key: str, value: str) -> None:
    """Set KEY to VALUE."""
    click.echo(f"Set {key} = {value}")


if __name__ == "__main__":
    cli()
