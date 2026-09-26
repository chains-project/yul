"""Command-line entry point for taskcli, built on Click."""

from __future__ import annotations

from pathlib import Path

import click

from .storage import load_tasks, next_id, save_tasks

DEFAULT_STORE = Path.home() / ".taskcli.json"


@click.group()
@click.option(
    "--store",
    type=click.Path(dir_okay=False, path_type=Path),
    default=DEFAULT_STORE,
    show_default=True,
    help="Path to the JSON file tasks are stored in.",
)
@click.version_option(package_name="taskcli")
@click.pass_context
def cli(ctx: click.Context, store: Path) -> None:
    """Manage a simple to-do list from the terminal."""
    ctx.obj = {"store": store}


@cli.command()
@click.argument("title")
@click.option(
    "-p",
    "--priority",
    type=click.Choice(["low", "medium", "high"], case_sensitive=False),
    default="medium",
    show_default=True,
    help="Priority of the task.",
)
@click.pass_context
def add(ctx: click.Context, title: str, priority: str) -> None:
    """Add a new task with the given TITLE."""
    store = ctx.obj["store"]
    tasks = load_tasks(store)
    from .storage import Task

    task = Task(id=next_id(tasks), title=title, priority=priority.lower())
    tasks.append(task)
    save_tasks(store, tasks)
    click.echo(f"Added task #{task.id}: {task.title} [{task.priority}]")


@cli.command(name="list")
@click.option("--all", "show_all", is_flag=True, help="Include completed tasks.")
@click.pass_context
def list_tasks(ctx: click.Context, show_all: bool) -> None:
    """List tasks, hiding completed ones by default."""
    tasks = load_tasks(ctx.obj["store"])
    if not show_all:
        tasks = [t for t in tasks if not t.done]
    if not tasks:
        click.echo("No tasks found.")
        return
    for task in tasks:
        status = "x" if task.done else " "
        click.echo(f"[{status}] #{task.id} ({task.priority}) {task.title}")


@cli.command()
@click.argument("task_id", type=int)
@click.pass_context
def done(ctx: click.Context, task_id: int) -> None:
    """Mark task TASK_ID as done."""
    store = ctx.obj["store"]
    tasks = load_tasks(store)
    for task in tasks:
        if task.id == task_id:
            task.done = True
            save_tasks(store, tasks)
            click.echo(f"Marked task #{task_id} as done.")
            return
    raise click.ClickException(f"No task with id {task_id}.")


@cli.command()
@click.argument("task_id", type=int)
@click.confirmation_option(prompt="Are you sure you want to delete this task?")
@click.pass_context
def remove(ctx: click.Context, task_id: int) -> None:
    """Remove task TASK_ID."""
    store = ctx.obj["store"]
    tasks = load_tasks(store)
    remaining = [t for t in tasks if t.id != task_id]
    if len(remaining) == len(tasks):
        raise click.ClickException(f"No task with id {task_id}.")
    save_tasks(store, remaining)
    click.echo(f"Removed task #{task_id}.")


if __name__ == "__main__":
    cli()
