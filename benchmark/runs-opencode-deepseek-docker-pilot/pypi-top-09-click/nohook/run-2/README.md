# taskcli

A small command-line task manager built on Python's standard-library
[`argparse`](https://docs.python.org/3/library/argparse.html). It demonstrates a
typical multi-command CLI: global options, subcommands, flags, typed arguments,
choices, and validation.

## Features

- Subcommands: `add`, `list`, `done`, `remove`
- Global options: `--data-file`, `--verbose`, `--version`
- Typed options with validation (`--due YYYY-MM-DD`, positive integer ids)
- Choice-restricted values (`--priority low|medium|high`)
- JSON storage with an atomic write, plus `list --json` for scripting
- No third-party runtime dependencies

## Install

From the project root, in a virtual environment:

```console
python -m venv .venv
. .venv/bin/activate
pip install -e .
```

This installs the `task` console script. You can also run the package without
installing it:

```console
PYTHONPATH=src python -m taskcli --help
```

## Usage

```console
$ task add "write the report" --priority high --due 2030-01-02
Added task 1: write the report

$ task add "buy milk"
Added task 2: buy milk

$ task list
[ ]   1  high    write the report  due 2030-01-02
[ ]   2  medium  buy milk

$ task done 2
Task 2 completed: buy milk

$ task list
[ ]   1  high    write the report  due 2030-01-02

$ task list --all --json
[
  {
    "id": 1,
    "title": "write the report",
    "priority": "high",
    "due": "2030-01-02",
    "done": false
  },
  ...
]

$ task remove 1
Removed task 1: write the report
```

Run `task <command> --help` for command-specific options.

### Data location

Tasks are stored as JSON. The location is resolved in this order:

1. `--data-file PATH`
2. the `TASKCLI_DATA` environment variable
3. `$XDG_DATA_HOME/taskcli/tasks.json` (or `~/.local/share/taskcli/tasks.json`)

## Project layout

```
src/taskcli/
  cli.py           # argument parser wiring and main() entry point
  context.py       # shared runtime context passed to commands
  models.py        # Task dataclass and priorities
  storage.py       # JSON load/save and data-file resolution
  commands/
    _common.py     # shared argument validators and lookup helpers
    add.py
    list.py
    done.py
    remove.py
tests/
```

Each command module exposes `add_parser(subparsers)` and `run(args, ctx)`, and
is registered in `taskcli/cli.py`. Add a new module and append it to `COMMANDS`
to extend the tool.

## Development

Run the test suite (no extra dependencies required):

```console
python -m unittest discover -s tests -t . -v
```

Or with pytest if you have it:

```console
pip install -e ".[dev]"
pytest
```
