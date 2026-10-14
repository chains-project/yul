# mycli

A command-line tool with multiple subcommands, built on the standard library's `argparse`.

## Install

```sh
python -m venv .venv && . .venv/bin/activate
pip install -e '.[dev]'
```

## Usage

```sh
mycli --help
mycli greet Ada Linus --greeting Hi --times 2 --shout
mycli stats README.md pyproject.toml
cat file.txt | mycli stats --format json --only words
python -m mycli --version
```

Global options (`-v/-vv`, `-q`, `--version`) go before the subcommand.

## Adding a subcommand

1. Create `src/mycli/commands/<name>.py` with a `register(subparsers)` function that
   adds a parser and calls `parser.set_defaults(func=run)`.
2. Write `run(args) -> int` returning the exit code.
3. Add `<name>.register` to `COMMANDS` in `src/mycli/commands/__init__.py`.

## Test

```sh
pytest
```
