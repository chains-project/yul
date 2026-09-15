from pathlib import Path

import click

from taskcli import __version__
from taskcli.storage import DEFAULT_STORE_PATH, load_tasks, save_tasks


@click.group()
@click.version_option(version=__version__, prog_name="taskcli")
@click.option(
    "--store",
    type=click.Path(dir_okay=False, path_type=Path),
    default=DEFAULT_STORE_PATH,
    show_default=True,
    help="Path to the JSON file used to store tasks.",
)
@click.pass_context
def cli(ctx: click.Context, store: Path) -> None:
    """taskcli - a small command-line task manager."""
    ctx.ensure_object(dict)
    ctx.obj["store"] = store


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
    """Add a new task with TITLE."""
    store = ctx.obj["store"]
    tasks = load_tasks(store)
    tasks.append({"title": title, "priority": priority.lower(), "done": False})
    save_tasks(tasks, store)
    click.echo(f"Added task #{len(tasks)}: {title} [{priority.lower()}]")


@cli.command(name="list")
@click.option("--all", "show_all", is_flag=True, help="Include completed tasks.")
@click.pass_context
def list_tasks(ctx: click.Context, show_all: bool) -> None:
    """List tasks."""
    store = ctx.obj["store"]
    tasks = load_tasks(store)
    if not tasks:
        click.echo("No tasks yet.")
        return

    for i, task in enumerate(tasks, start=1):
        if task["done"] and not show_all:
            continue
        status = "x" if task["done"] else " "
        click.echo(f"[{status}] #{i} ({task['priority']}) {task['title']}")


@cli.command()
@click.argument("task_id", type=int)
@click.pass_context
def done(ctx: click.Context, task_id: int) -> None:
    """Mark task TASK_ID as complete."""
    store = ctx.obj["store"]
    tasks = load_tasks(store)
    if not 1 <= task_id <= len(tasks):
        raise click.ClickException(f"No task #{task_id}")
    tasks[task_id - 1]["done"] = True
    save_tasks(tasks, store)
    click.echo(f"Marked #{task_id} as done.")


@cli.command()
@click.argument("task_id", type=int)
@click.confirmation_option(prompt="Are you sure you want to delete this task?")
@click.pass_context
def remove(ctx: click.Context, task_id: int) -> None:
    """Remove task TASK_ID."""
    store = ctx.obj["store"]
    tasks = load_tasks(store)
    if not 1 <= task_id <= len(tasks):
        raise click.ClickException(f"No task #{task_id}")
    removed = tasks.pop(task_id - 1)
    save_tasks(tasks, store)
    click.echo(f"Removed #{task_id}: {removed['title']}")


if __name__ == "__main__":
    cli()
