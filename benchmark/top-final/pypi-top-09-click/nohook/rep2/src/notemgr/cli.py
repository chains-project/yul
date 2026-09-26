from pathlib import Path

import click

from notemgr.store import DEFAULT_STORE, load_notes, next_id, save_notes


@click.group()
@click.option(
    "--store",
    type=click.Path(dir_okay=False, path_type=Path),
    default=DEFAULT_STORE,
    show_default=True,
    help="Path to the notes storage file.",
)
@click.pass_context
def cli(ctx: click.Context, store: Path) -> None:
    """A simple command-line note manager."""
    ctx.obj = {"store": store}


@cli.command()
@click.argument("text")
@click.option("--tag", "-t", multiple=True, help="Tag to attach to the note (repeatable).")
@click.pass_context
def add(ctx: click.Context, text: str, tag: tuple[str, ...]) -> None:
    """Add a new note."""
    store = ctx.obj["store"]
    notes = load_notes(store)
    note = {"id": next_id(notes), "text": text, "tags": list(tag), "done": False}
    notes.append(note)
    save_notes(store, notes)
    click.echo(f"Added note #{note['id']}")


@cli.command(name="list")
@click.option("--tag", "-t", help="Only show notes with this tag.")
@click.option("--all", "show_all", is_flag=True, help="Include completed notes.")
@click.pass_context
def list_notes(ctx: click.Context, tag: str | None, show_all: bool) -> None:
    """List notes."""
    notes = load_notes(ctx.obj["store"])
    if tag:
        notes = [n for n in notes if tag in n["tags"]]
    if not show_all:
        notes = [n for n in notes if not n["done"]]

    if not notes:
        click.echo("No notes found.")
        return

    for note in notes:
        status = "x" if note["done"] else " "
        tags = f" [{', '.join(note['tags'])}]" if note["tags"] else ""
        click.echo(f"[{status}] #{note['id']} {note['text']}{tags}")


@cli.command()
@click.argument("note_id", type=int)
@click.pass_context
def done(ctx: click.Context, note_id: int) -> None:
    """Mark a note as done."""
    store = ctx.obj["store"]
    notes = load_notes(store)
    for note in notes:
        if note["id"] == note_id:
            note["done"] = True
            save_notes(store, notes)
            click.echo(f"Marked note #{note_id} as done")
            return
    raise click.ClickException(f"No note with id {note_id}")


@cli.command()
@click.argument("note_id", type=int)
@click.confirmation_option(prompt="Are you sure you want to delete this note?")
@click.pass_context
def remove(ctx: click.Context, note_id: int) -> None:
    """Remove a note."""
    store = ctx.obj["store"]
    notes = load_notes(store)
    filtered = [n for n in notes if n["id"] != note_id]
    if len(filtered) == len(notes):
        raise click.ClickException(f"No note with id {note_id}")
    save_notes(store, filtered)
    click.echo(f"Removed note #{note_id}")


if __name__ == "__main__":
    cli()
