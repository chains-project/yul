"""Deploy command subcommand."""

import click


@click.command()
@click.argument("environment", type=click.Choice(["staging", "production"]))
@click.option("--region", "-r", type=str, default="us-east-1", help="Deployment region.")
@click.option("--dry-run", is_flag=True, help="Preview changes without applying.")
@click.option("--tag", "-t", type=str, default=None, help="Tag to deploy.")
@click.pass_context
def deploy(ctx, environment, region, dry_run, tag):
    """Deploy to an environment."""
    verbose = ctx.obj.get("verbose", False)
    click.echo(f"Deploying to: {environment}")
    click.echo(f"Region: {region}")
    if tag:
        click.echo(f"Tag: {tag}")
    if dry_run:
        click.echo("Dry run - no changes applied.")
    if verbose:
        click.echo("Verbose mode on.")