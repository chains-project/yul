"""Command-line task manager.

Usage:
    task add "Write report" --priority high --tag work
    task list --pending
    task done 1 2
    task remove 3
"""

from __future__ import annotations

from pathlib import Path

import click

from .storage import DEFAULT_TASKS_FILE, load_tasks, next_id, save_tasks

PRIORITIES = ["low", "medium", "high"]


@click.group()
@click.option(
    "--tasks-file",
    type=click.Path(dir_okay=False, path_type=Path),
    default=DEFAULT_TASKS_FILE,
    show_default=True,
    envvar="TASKCLI_FILE",
    help="Path to the JSON file tasks are stored in.",
)
@click.version_option()
@click.pass_context
def cli(ctx: click.Context, tasks_file: Path) -> None:
    """A simple command-line task manager."""
    ctx.ensure_object(dict)
    ctx.obj["tasks_file"] = tasks_file


@cli.command()
@click.argument("description")
@click.option(
    "-p",
    "--priority",
    type=click.Choice(PRIORITIES, case_sensitive=False),
    default="medium",
    show_default=True,
    help="Priority of the task.",
)
@click.option(
    "-t",
    "--tag",
    "tags",
    multiple=True,
    help="Tag to attach to the task. Can be passed multiple times.",
)
@click.pass_context
def add(ctx: click.Context, description: str, priority: str, tags: tuple[str, ...]) -> None:
    """Add a new task."""
    tasks_file = ctx.obj["tasks_file"]
    tasks = load_tasks(tasks_file)
    task = {
        "id": next_id(tasks),
        "description": description,
        "priority": priority.lower(),
        "tags": list(tags),
        "done": False,
    }
    tasks.append(task)
    save_tasks(tasks_file, tasks)
    click.echo(f"Added task #{task['id']}: {description}")


@cli.command(name="list")
@click.option("--all", "show_all", is_flag=True, help="Show completed tasks too.")
@click.option("--tag", "tag_filter", default=None, help="Only show tasks with this tag.")
@click.option(
    "--priority",
    "priority_filter",
    type=click.Choice(PRIORITIES, case_sensitive=False),
    default=None,
    help="Only show tasks with this priority.",
)
@click.pass_context
def list_tasks(
    ctx: click.Context,
    show_all: bool,
    tag_filter: str | None,
    priority_filter: str | None,
) -> None:
    """List tasks."""
    tasks = load_tasks(ctx.obj["tasks_file"])

    if not show_all:
        tasks = [t for t in tasks if not t["done"]]
    if tag_filter:
        tasks = [t for t in tasks if tag_filter in t["tags"]]
    if priority_filter:
        tasks = [t for t in tasks if t["priority"] == priority_filter.lower()]

    if not tasks:
        click.echo("No tasks found.")
        return

    for task in tasks:
        status = "x" if task["done"] else " "
        tags = f" ({', '.join(task['tags'])})" if task["tags"] else ""
        click.echo(f"[{status}] #{task['id']} [{task['priority']}] {task['description']}{tags}")


@cli.command()
@click.argument("task_ids", type=int, nargs=-1, required=True)
@click.pass_context
def done(ctx: click.Context, task_ids: tuple[int, ...]) -> None:
    """Mark one or more tasks as done."""
    tasks_file = ctx.obj["tasks_file"]
    tasks = load_tasks(tasks_file)
    by_id = {t["id"]: t for t in tasks}

    for task_id in task_ids:
        task = by_id.get(task_id)
        if task is None:
            raise click.ClickException(f"No task with id {task_id}")
        task["done"] = True
        click.echo(f"Completed task #{task_id}")

    save_tasks(tasks_file, tasks)


@cli.command()
@click.argument("task_ids", type=int, nargs=-1, required=True)
@click.option("--yes", is_flag=True, help="Skip the confirmation prompt.")
@click.pass_context
def remove(ctx: click.Context, task_ids: tuple[int, ...], yes: bool) -> None:
    """Remove one or more tasks."""
    tasks_file = ctx.obj["tasks_file"]
    tasks = load_tasks(tasks_file)
    ids = set(task_ids)

    missing = ids - {t["id"] for t in tasks}
    if missing:
        raise click.ClickException(f"No task(s) with id(s): {', '.join(map(str, sorted(missing)))}")

    if not yes:
        click.confirm(f"Remove {len(ids)} task(s)?", abort=True)

    tasks = [t for t in tasks if t["id"] not in ids]
    save_tasks(tasks_file, tasks)
    click.echo(f"Removed {len(ids)} task(s).")


if __name__ == "__main__":
    cli()
