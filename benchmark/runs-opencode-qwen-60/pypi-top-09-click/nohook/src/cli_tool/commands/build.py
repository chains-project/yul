"""Build command subcommand."""

import click


@click.command()
@click.argument("target", type=click.Choice(["debug", "release"]), default="release")
@click.option("--output", "-o", type=click.Path(), default="./dist", help="Output directory.")
@click.option("--jobs", "-j", type=int, default=1, help="Number of parallel jobs.")
@click.option("--force", "-f", is_flag=True, help="Force rebuild.")
@click.pass_context
def build(ctx, target, output, jobs, force):
    """Build the project."""
    verbose = ctx.obj.get("verbose", False)
    click.echo(f"Building target: {target}")
    click.echo(f"Output directory: {output}")
    click.echo(f"Parallel jobs: {jobs}")
    if force:
        click.echo("Force rebuild enabled.")
    if verbose:
        click.echo("Verbose mode on.")