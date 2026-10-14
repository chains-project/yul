# mycli

A command-line tool with multiple subcommands, built on the standard library's `argparse`
(no runtime dependencies).

## Install

```sh
python -m venv .venv && source .venv/bin/activate
pip install -e '.[dev]'
```

## Usage

```sh
mycli --help
mycli --version
mycli [-v | -vv | -q] <command> ...

mycli greet                          # Hello, world!
mycli greet Ada --shout -n 3         # HELLO, ADA! (x3)
mycli greet Ada --greeting Hi

mycli count file.txt other.txt       # lines, words, chars (like wc)
mycli count -l -w file.txt           # only selected fields
cat file.txt | mycli count --format json
```

`python -m mycli ...` also works.

Exit codes: `0` success, `1` runtime error (e.g. missing file), `2` usage error,
`130` interrupted.

## Layout

```
src/mycli/
  cli.py            top-level parser, global options, logging, error handling
  errors.py         CLIError -> clean message + exit code (no traceback)
  commands/
    __init__.py     COMMANDS registry
    greet.py        `greet` subcommand
    count.py        `count` subcommand
tests/              pytest tests
```

## Adding a subcommand

1. Create `src/mycli/commands/<name>.py` with `register(subparsers)` (calling
   `parser.set_defaults(func=run)`) and `run(args) -> int`.
2. Add the module to `COMMANDS` in `src/mycli/commands/__init__.py`.
3. Raise `CLIError` for expected failures.

## Development

```sh
pytest
ruff check . && ruff format .
```
