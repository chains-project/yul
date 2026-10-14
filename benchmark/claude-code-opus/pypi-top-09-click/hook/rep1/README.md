# mycli

A command-line tool with subcommands, built on the standard library's `argparse`.

## Setup

```sh
uv venv && source .venv/bin/activate
uv pip install -e '.[dev]'
```

(or `python -m venv .venv && pip install -e '.[dev]'`)

## Usage

```sh
mycli --help
mycli greet Ada Linus -g Hi -n 2 --style shout
mycli -v count README.md pyproject.toml
cat README.md | mycli count --words --json
python -m mycli --version
```

Global options (`-v/--verbose`, `-q/--quiet`, `--version`) go **before** the subcommand.

## Adding a command

1. Create `src/mycli/commands/<name>.py` with a `register(subparsers)` function that
   adds a parser and calls `parser.set_defaults(handler=run)`.
2. Implement `run(args) -> int` returning an exit code. Raise `mycli.errors.CommandError`
   for expected failures (it prints a clean error message instead of a traceback).
3. Add `<name>.register` to `COMMANDS` in `src/mycli/commands/__init__.py`.

## Development

```sh
pytest
ruff check . && ruff format .
```
