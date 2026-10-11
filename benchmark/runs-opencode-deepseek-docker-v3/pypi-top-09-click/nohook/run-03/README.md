# mytool

A small command-line tool with multiple subcommands, options and argument
parsing. Built with only the standard library (`argparse`), no runtime
dependencies.

## Features

- Top-level parser with `--version` and a global `-v/--verbose` flag.
- A subcommand registry: each command lives in `src/mytool/commands/`.
- Sample commands:
  - `greet` - positional and optional arguments, custom type validation.
  - `config` - nested subcommands (`get`/`set`/`list`) backed by a JSON file.
- Test suite using `pytest`.

## Project layout

```
pyproject.toml
src/mytool/
  __init__.py
  __main__.py
  cli.py
  commands/
    __init__.py
    greet.py
    config.py
tests/
  test_cli.py
```

## Install

Using [uv](https://docs.astral.sh/uv/):

```bash
uv sync --extra dev
```

Or with plain `pip`:

```bash
python -m pip install -e ".[dev]"
```

## Usage

```bash
mytool --help
mytool greet --help
mytool greet Ada --uppercase --repeat 3
mytool config set color blue
mytool config get color
mytool config list
```

You can also run it without installing:

```bash
python -m mytool greet
```

## Adding a command

1. Create `src/mytool/commands/<name>.py` exposing a
   `register(subparsers, common)` function and a `run(args)` handler.
2. Add `"<name>"` to `MODULES` in `src/mytool/commands/__init__.py`.

## Tests

```bash
uv run pytest
```
