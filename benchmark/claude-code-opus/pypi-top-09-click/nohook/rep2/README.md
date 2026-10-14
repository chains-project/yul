# todo-cli

A small command-line todo manager, built on the standard library's `argparse`
(no runtime dependencies).

## Install

```sh
uv venv && uv pip install -e '.[dev]'   # or: python -m venv .venv && pip install -e '.[dev]'
```

## Usage

```sh
todo add buy milk -p high -t shop     # add with priority and tags (-t is repeatable)
todo list                             # open items  (alias: ls)
todo list -a --sort priority          # include completed, sorted
todo list --tag shop --format json    # filter, machine-readable output
todo done 1 2                         # complete items (--undo to reopen)
todo remove 3 -y                      # delete without prompting (alias: rm)
todo clear --dry-run                  # preview deleting all completed items
todo --help / todo <command> --help
```

Global options `-f/--file PATH` and `-q/--quiet` work before or after the
subcommand. The store defaults to `$TODO_FILE` or `~/.todo.json`.

Also runnable as `python -m todo_cli`.

## Development

```sh
pytest
ruff check . && ruff format .
```

## Layout

```
src/todo_cli/
  cli.py       # parser construction (build_parser) and subcommand handlers
  store.py     # JSON persistence
  __main__.py  # python -m entry point
tests/         # pytest suite
```

To add a subcommand: write a `cmd_<name>(args, store) -> int` handler, then
register it in `build_parser()` with `sub.add_parser(..., parents=[common])`
and `set_defaults(func=cmd_<name>)`.
