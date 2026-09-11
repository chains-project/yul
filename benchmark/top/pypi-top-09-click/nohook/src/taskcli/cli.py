from pathlib import Path

import click

from taskcli.storage import DEFAULT_PATH, load_tasks, save_tasks

PRIORITIES = ["low", "medium", "high"]


@click.group()
@click.option(
    "-f",
    "--file",
    "store",
    type=click.Path(dir_okay=False, path_type=Path),
    default=DEFAULT_PATH,
    show_default=True,
    help="Path to the task storage file.",
)
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose output.")
@click.version_option()
@click.pass_context
def cli(ctx: click.Context, store: Path, verbose: bool) -> None:
    """A simple command-line task manager."""
    ctx.ensure_object(dict)
    ctx.obj["store"] = store
    ctx.obj["verbose"] = verbose


@cli.command()
@click.argument("description")
@click.option(
    "-p",
    "--priority",
    type=click.Choice(PRIORITIES, case_sensitive=False),
    default="medium",
    show_default=True,
    help="Task priority.",
)
@click.pass_context
def add(ctx: click.Context, description: str, priority: str) -> None:
    """Add a new task with DESCRIPTION."""
    store = ctx.obj["store"]
    tasks = load_tasks(store)
    task = {"id": len(tasks) + 1, "description": description, "priority": priority, "done": False}
    tasks.append(task)
    save_tasks(store, tasks)
    if ctx.obj["verbose"]:
        click.echo(f"Saved to {store}")
    click.echo(f"Added task #{task['id']}: {description} [{priority}]")


@cli.command(name="list")
@click.option("--all/--pending", default=False, help="Show all tasks or only pending ones.")
@click.pass_context
def list_tasks(ctx: click.Context, all: bool) -> None:
    """List tasks."""
    tasks = load_tasks(ctx.obj["store"])
    if not all:
        tasks = [t for t in tasks if not t["done"]]
    if not tasks:
        click.echo("No tasks found.")
        return
    for task in tasks:
        status = "x" if task["done"] else " "
        click.echo(f"[{status}] #{task['id']} ({task['priority']}) {task['description']}")


@cli.command()
@click.argument("task_id", type=int)
@click.pass_context
def done(ctx: click.Context, task_id: int) -> None:
    """Mark task TASK_ID as done."""
    store = ctx.obj["store"]
    tasks = load_tasks(store)
    for task in tasks:
        if task["id"] == task_id:
            task["done"] = True
            save_tasks(store, tasks)
            click.echo(f"Marked task #{task_id} as done.")
            return
    raise click.ClickException(f"No task with id {task_id}")


@cli.command()
@click.argument("task_id", type=int)
@click.confirmation_option(prompt="Are you sure you want to remove this task?")
@click.pass_context
def remove(ctx: click.Context, task_id: int) -> None:
    """Remove task TASK_ID."""
    store = ctx.obj["store"]
    tasks = load_tasks(store)
    remaining = [t for t in tasks if t["id"] != task_id]
    if len(remaining) == len(tasks):
        raise click.ClickException(f"No task with id {task_id}")
    save_tasks(store, remaining)
    click.echo(f"Removed task #{task_id}.")


if __name__ == "__main__":
    cli()
