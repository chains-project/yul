from __future__ import annotations

from pathlib import Path

import click

from tasker.store import TaskStore

DEFAULT_STORE_PATH = Path.home() / ".tasker" / "tasks.json"


@click.group()
@click.option(
    "--store-path",
    type=click.Path(path_type=Path),
    default=DEFAULT_STORE_PATH,
    show_default=True,
    help="Path to the JSON file used to persist tasks.",
)
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose output.")
@click.version_option()
@click.pass_context
def cli(ctx: click.Context, store_path: Path, verbose: bool) -> None:
    """tasker: a small command-line task manager."""
    ctx.ensure_object(dict)
    ctx.obj["store"] = TaskStore.load(store_path)
    ctx.obj["verbose"] = verbose


@cli.command()
@click.argument("text")
@click.option(
    "-p",
    "--priority",
    type=click.Choice(["low", "normal", "high"]),
    default="normal",
    show_default=True,
    help="Priority level for the task.",
)
@click.pass_context
def add(ctx: click.Context, text: str, priority: str) -> None:
    """Add a new task."""
    store: TaskStore = ctx.obj["store"]
    task = store.add(text, priority)
    click.echo(f"Added task #{task.id}: {task.text} [{task.priority}]")


@cli.command(name="list")
@click.option("-a", "--all", "show_all", is_flag=True, help="Include completed tasks.")
@click.pass_context
def list_tasks(ctx: click.Context, show_all: bool) -> None:
    """List tasks."""
    store: TaskStore = ctx.obj["store"]
    tasks = store.tasks if show_all else [t for t in store.tasks if not t.done]
    if not tasks:
        click.echo("No tasks found.")
        return
    for task in tasks:
        status = "x" if task.done else " "
        click.echo(f"[{status}] #{task.id} ({task.priority}) {task.text}")


@cli.command()
@click.argument("task_id", type=int)
@click.pass_context
def done(ctx: click.Context, task_id: int) -> None:
    """Mark a task as done."""
    store: TaskStore = ctx.obj["store"]
    if store.mark_done(task_id):
        click.echo(f"Task #{task_id} marked as done.")
    else:
        raise click.ClickException(f"No task with id {task_id}.")


@cli.command()
@click.argument("task_id", type=int)
@click.confirmation_option(prompt="Are you sure you want to remove this task?")
@click.pass_context
def remove(ctx: click.Context, task_id: int) -> None:
    """Remove a task."""
    store: TaskStore = ctx.obj["store"]
    if store.remove(task_id):
        click.echo(f"Task #{task_id} removed.")
    else:
        raise click.ClickException(f"No task with id {task_id}.")


if __name__ == "__main__":
    cli()
