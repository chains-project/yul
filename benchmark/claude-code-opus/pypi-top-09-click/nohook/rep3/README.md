# mycli

A command-line tool with multiple subcommands, built on the standard library's
`argparse` (no runtime dependencies).

## Install

```sh
python -m venv .venv && . .venv/bin/activate
pip install -e '.[dev]'
```

## Usage

```sh
mycli --help
mycli greet Ada --times 2 --shout
mycli count -l README.md pyproject.toml
echo "hello world" | mycli count -w
mycli config set color blue
mycli config get color
mycli config list --json
mycli --config ./local.json config list
```

You can also run it without installing: `PYTHONPATH=src python -m mycli --help`.

Global options (`-v/--verbose`, `-q/--quiet`, `--config PATH`, `--version`)
come **before** the subcommand.

## Layout

```
src/mycli/
  cli.py            # top-level parser, global options, main()
  errors.py         # CLIError: user-facing errors (exit code 1, no traceback)
  commands/
    greet.py        # simple command with positional + options
    count.py        # file/stdin input, boolean flags
    config.py       # nested subcommands (get/set/unset/list)
tests/
```

## Adding a command

1. Create `src/mycli/commands/<name>.py` with a `register(subparsers)` function
   that calls `subparsers.add_parser(...)`, adds arguments, and binds a handler
   with `set_defaults(func=run)`.
2. Add the module to `COMMANDS` in `src/mycli/cli.py`.
3. Handlers receive the parsed `argparse.Namespace` and return an exit code.
   Raise `CLIError` for expected failures.

## Exit codes

| Code | Meaning                         |
|------|---------------------------------|
| 0    | success                         |
| 1    | command error (`CLIError`)      |
| 2    | usage error (bad arguments)     |
| 130  | interrupted (Ctrl-C)            |

## Tests

```sh
pytest
```
