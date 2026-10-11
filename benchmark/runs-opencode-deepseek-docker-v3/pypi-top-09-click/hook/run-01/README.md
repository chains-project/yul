# clitool

A small command-line tool demonstrating a multi-subcommand `argparse` layout:
positional arguments, optional flags, nested subcommands, persisted config, and
typed, testable command handlers.

## Requirements

- Python 3.10+
- [`uv`](https://docs.astral.sh/uv/) (recommended) or `pip`

## Setup

```bash
uv sync --extra dev
```

With plain `pip`:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

```bash
uv run clitool --help
uv run clitool greet Ada --count 2 --uppercase
uv run clitool calc add 1 2 3
uv run clitool calc div 10 4
uv run clitool config set color blue
uv run clitool config list
uv run clitool info --json
```

The tool can also be run as a module:

```bash
uv run python -m clitool greet world
```

### Global options

| Option | Description |
| --- | --- |
| `--version` | Print the version and exit. |
| `-v`, `--verbose` | Increase verbosity (`-v` = INFO, `-vv` = DEBUG). |
| `-q`, `--quiet` | Only show errors. |

## Commands

| Command | Description |
| --- | --- |
| `greet [NAME]` | Print a greeting (`-g/--greeting`, `-c/--count`, `-u/--uppercase`). |
| `calc {add,sub,mul,div} N...` | Arithmetic over one or more numbers. |
| `config {get,set,unset,list}` | Read/write a JSON config file (`-f/--file`). |
| `info [--json]` | Show version and environment information. |

## Project layout

```
src/clitool/
  __init__.py        version
  __main__.py        python -m clitool
  cli.py             parser construction + dispatch
  commands/
    greet.py         positional + options
    calc.py          nested subcommands
    config.py        persisted state
    info.py          forms of output
tests/test_cli.py
```

Each command module defines `register(subparsers)` to attach its parser and
`run(args) -> int` as the handler (wired via `set_defaults(handler=...)`).
To add a command, create a module and register it in `cli.build_parser()`.

## Development

```bash
uv run pytest        # tests
uv run ruff check .  # lint
uv run ruff format . # format
uv run mypy          # type check
```

## License

MIT
