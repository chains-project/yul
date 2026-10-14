# mytool

A command-line tool with multiple subcommands, built on the standard library's
`argparse` (no runtime dependencies).

## Install

```sh
python -m venv .venv && . .venv/bin/activate
pip install -e '.[dev]'
```

## Usage

```sh
mytool --help
mytool greet Ada Linus --greeting Hi --style shout -n 2
mytool stats README.md src/mytool/cli.py --format json
cat file.txt | mytool stats
mytool config set color blue
mytool config get color
mytool config list
mytool -vv config --file ./local.json list
```

Global options (`-v/--verbose`, `-q/--quiet`, `--version`) go **before** the
subcommand. `python -m mytool` works too.

Exit codes: `0` success, `1` runtime error, `2` usage error, `130` interrupted.

## Layout

```
src/mytool/
  cli.py            # top-level parser, global options, error handling
  errors.py         # CLIError: raise for user-facing failures
  commands/         # one module per subcommand
    greet.py        # positionals, typed options, choices
    stats.py        # file/stdin input, output formats
    config.py       # nested subcommands (get/set/unset/list)
tests/
```

## Adding a command

1. Create `src/mytool/commands/<name>.py` with a `register(subparsers)` function
   that calls `subparsers.add_parser(...)`, adds arguments, and sets
   `func=run` via `set_defaults`.
2. Write `run(args) -> int`; raise `CLIError` for expected failures.
3. Add the module to `COMMANDS` in `cli.py`.

## Tests

```sh
pytest
```
