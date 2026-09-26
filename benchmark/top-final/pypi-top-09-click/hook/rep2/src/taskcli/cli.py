from pathlib import Path

import click

from taskcli import storage
from taskcli.storage import DEFAULT_STORE, Task

PRIORITIES = ["low", "normal", "high"]


@click.group()
@click.option(
    "--store",
    type=click.Path(path_type=Path),
    default=DEFAULT_STORE,
    show_default=True,
    help="Path to the JSON file tasks are stored in.",
)
@click.version_option(package_name="taskcli")
@click.pass_context
def cli(ctx: click.Context, store: Path) -> None:
    """taskcli: a small command-line task manager."""
    ctx.ensure_object(dict)
    ctx.obj["store"] = store


@cli.command()
@click.argument("title")
@click.option(
    "--priority",
    type=click.Choice(PRIORITIES),
    default="normal",
    show_default=True,
    help="Task priority.",
)
@click.pass_context
def add(ctx: click.Context, title: str, priority: str) -> None:
    """Add a new task."""
    store = ctx.obj["store"]
    tasks = storage.load(store)
    task = Task(id=storage.next_id(tasks), title=title, priority=priority)
    tasks.append(task)
    storage.save(tasks, store)
    click.echo(f"Added task #{task.id}: {task.title} [{task.priority}]")


@cli.command(name="list")
@click.option("--all", "show_all", is_flag=True, help="Include completed tasks.")
@click.option(
    "--priority",
    type=click.Choice(PRIORITIES),
    default=None,
    help="Only show tasks with this priority.",
)
@click.pass_context
def list_tasks(ctx: click.Context, show_all: bool, priority: str | None) -> None:
    """List tasks."""
    tasks = storage.load(ctx.obj["store"])
    if not show_all:
        tasks = [t for t in tasks if not t.done]
    if priority:
        tasks = [t for t in tasks if t.priority == priority]

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
    """Mark a task as done."""
    store = ctx.obj["store"]
    tasks = storage.load(store)
    for task in tasks:
        if task.id == task_id:
            task.done = True
            storage.save(tasks, store)
            click.echo(f"Marked task #{task.id} as done.")
            return
    raise click.ClickException(f"No task with id {task_id}")


@cli.command()
@click.argument("task_id", type=int)
@click.confirmation_option(prompt="Are you sure you want to delete this task?")
@click.pass_context
def remove(ctx: click.Context, task_id: int) -> None:
    """Remove a task."""
    store = ctx.obj["store"]
    tasks = storage.load(store)
    remaining = [t for t in tasks if t.id != task_id]
    if len(remaining) == len(tasks):
        raise click.ClickException(f"No task with id {task_id}")
    storage.save(remaining, store)
    click.echo(f"Removed task #{task_id}.")


if __name__ == "__main__":
    cli()
