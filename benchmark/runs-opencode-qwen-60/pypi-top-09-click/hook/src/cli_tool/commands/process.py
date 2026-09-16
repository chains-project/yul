"""Process subcommand with callback validation and file handling."""

import click
import os


def validate_size(ctx, param, value):
    """Custom callback to validate and normalize size values."""
    if value is None:
        return None
    size_str = str(value).strip().lower()
    multipliers = {"k": 1024, "m": 1048576, "g": 1073741824}
    if size_str and size_str[-1] in multipliers:
        try:
            number = float(size_str[:-1])
            return int(number * multipliers[size_str[-1]])
        except ValueError:
            raise click.BadParameter(
                f"Invalid size format: {value}. Use numbers with optional k/m/g suffix."
            )
    try:
        return int(value)
    except ValueError:
        raise click.BadParameter(
            f"Invalid size: {value}. Must be an integer or integer with suffix (e.g., 10k, 5m)."
        )


@click.command()
@click.argument("input_path", type=click.Path(exists=True, readable=True, dir_okay=False))
@click.option(
    "-o",
    "--output",
    type=click.Path(writable=True, dir_okay=False),
    default=None,
    help="Output file path. If not provided, prints to stdout.",
)
@click.option(
    "-s",
    "--size-limit",
    callback=validate_size,
    help="Maximum file size to process (e.g., 10k, 5m).",
)
@click.option(
    "-e",
    "--encoding",
    default="utf-8",
    help="File encoding.",
)
@click.option(
    "-n",
    "--lines",
    type=click.IntRange(min=1),
    default=None,
    help="Process only the first N lines.",
)
@click.option(
    "--quiet",
    "-q",
    is_flag=True,
    default=False,
    help="Suppress all output except errors.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Show what would be done without actually doing it.",
)
@click.pass_context
def process(ctx, input_path, output, size_limit, encoding, lines, quiet, dry_run):
    """Process a file with various constraints and options.

    INPUT_PATH is the path to the file to process.

    Examples:
        cli-tool process data.txt
        cli-tool process data.txt --output result.txt --lines 100
        cli-tool process data.txt --size-limit 10m --encoding latin-1
    """
    if not quiet:
        click.echo(f"Processing: {input_path}")

    file_size = os.path.getsize(input_path)
    if not quiet:
        click.echo(f"File size: {file_size:,} bytes")

    if size_limit and file_size > size_limit:
        raise click.BadParameter(
            f"File size ({file_size:,} bytes) exceeds limit ({size_limit:,} bytes).",
            ctx=ctx,
            param=None,
        )

    if dry_run:
        if not quiet:
            click.echo("[Dry run] Would process the file.")
        return

    try:
        with click.open_file(input_path, encoding=encoding, errors="replace") as f:
            if lines:
                content = "".join(f.readline() for _ in range(lines))
            else:
                content = f.read()
    except Exception as e:
        raise click.ClickException(f"Error reading file: {e}")

    if output:
        try:
            with click.open_file(output, "w", encoding=encoding) as f:
                f.write(content)
            if not quiet:
                click.echo(f"Output written to: {output}")
        except Exception as e:
            raise click.ClickException(f"Error writing file: {e}")
    else:
        click.echo(content, nl=False)