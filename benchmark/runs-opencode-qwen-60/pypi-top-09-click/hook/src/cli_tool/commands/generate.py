"""Generate subcommand with dynamic options and choices."""

import click
import random
import string


@click.command()
@click.argument("count", type=click.IntRange(min=1, max=1000), default=10)
@click.option(
    "--type",
    "item_type",
    type=click.Choice(["numbers", "letters", "uuid", "password"], case_sensitive=False),
    default="numbers",
    help="Type of items to generate.",
)
@click.option(
    "-l",
    "--length",
    type=click.IntRange(min=1, max=100),
    default=8,
    help="Length of generated items (applies to password/letters).",
)
@click.option(
    "-u",
    "--uppercase",
    is_flag=True,
    default=False,
    help="Use uppercase letters.",
)
@click.option(
    "--separator",
    default="\n",
    help="Separator between items (default: newline).",
)
@click.option(
    "-f",
    "--file",
    type=click.Path(writable=True),
    default=None,
    help="Write output to file instead of stdout.",
)
@click.option(
    "--seed",
    type=click.IntRange(min=0),
    default=None,
    help="Set random seed for reproducible output.",
)
@click.pass_context
def generate(ctx, count, item_type, length, uppercase, separator, file, seed):
    """Generate various types of items.

    COUNT is the number of items to generate (1-1000).

    Examples:
        cli-tool generate 5
        cli-tool generate --type password --length 12 --count 3
        cli-tool generate 10 --type uuid --separator ", "
    """
    if seed is not None:
        random.seed(seed)

    if file:
        with click.open_file(file, "w") as f:
            items = _generate_items(count, item_type, length, uppercase)
            f.write(separator.join(items) + separator)
        click.echo(f"Generated {count} {item_type} to: {file}")
    else:
        items = _generate_items(count, item_type, length, uppercase)
        click.echo(separator.join(items))


def _generate_items(count, item_type, length, uppercase):
    """Generate a list of items based on type."""
    if item_type == "numbers":
        return [str(random.randint(1, 99999)) for _ in range(count)]
    elif item_type == "letters":
        chars = string.ascii_uppercase if uppercase else string.ascii_lowercase
        return ["".join(random.choice(chars) for _ in range(length)) for _ in range(count)]
    elif item_type == "uuid":
        import uuid

        return [str(uuid.uuid4()) for _ in range(count)]
    elif item_type == "password":
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        return ["".join(random.choice(chars) for _ in range(length)) for _ in range(count)]
    return []