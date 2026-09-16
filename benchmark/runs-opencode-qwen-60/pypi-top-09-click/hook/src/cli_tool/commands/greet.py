"""Greet subcommand with options and arguments."""

import click


@click.command()
@click.argument("name")
@click.option(
    "-t",
    "--title",
    type=click.Choice(["Mr.", "Ms.", "Dr.", "Prof."], case_sensitive=False),
    default=None,
    help="Title to use before the name.",
)
@click.option(
    "-c",
    "--count",
    default=1,
    type=click.IntRange(min=1, max=100),
    help="Number of times to greet.",
)
@click.option(
    "-f",
    "--format",
    type=click.Choice(["text", "json"], case_sensitive=False),
    default="text",
    help="Output format.",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    default=False,
    help="Print additional greeting details.",
)
@click.option(
    "--uppercase",
    is_flag=True,
    default=False,
    help="Convert output to uppercase.",
)
@click.pass_context
def greet(ctx, name, title, count, format, verbose, uppercase):
    """Greet someone by name with configurable options.

    NAME is the person to greet.

    Examples:
        cli-tool greet Alice
        cli-tool greet Alice --title Dr. --count 3
        cli-tool greet Bob --format json
    """
    greeting = f"Hello"
    if title:
        greeting = f"Hello {title} {name}"
    else:
        greeting = f"Hello {name}"

    if verbose:
        click.echo(f"[Greeting {count} time(s)]")

    for i in range(count):
        if count > 1:
            output = f"Greeting #{i + 1}: {greeting}"
        else:
            output = greeting

        if uppercase:
            output = output.upper()

        if format == "json":
            import json

            output = json.dumps({"greeting": output, "index": i + 1})

        click.echo(output)