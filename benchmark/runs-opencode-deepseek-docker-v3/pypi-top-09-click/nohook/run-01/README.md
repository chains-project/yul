# clitool

A small, dependency-free Python command-line tool that demonstrates a
multi-command CLI: global options, nested subcommands, typed arguments,
validation, and a clean exit-code contract.

## Features

- **Global options** (`--version`, `-v/--verbose`, `-q/--quiet`, `--config`)
- **Multiple commands** with nested action subparsers (`tasks add`, `config set`, ...)
- Typed arguments (`type=int`, `choices=`, custom `positive_int`), repeatable
  flags (`action="append"`), and `nargs="+"` positional arguments
- JSON-backed state with clear, user-facing errors (no tracebacks)

## Layout

```
pyproject.toml
src/clitool/
  __init__.py
  __main__.py          # python -m clitool
  cli.py               # top-level parser + main()
  config.py            # JSON config load/save
  errors.py            # CliError
  commands/
    __init__.py        # COMMANDS registry
    hello.py
    tasks.py
    config_cmd.py
tests/test_cli.py
```

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

```bash
clitool --help
clitool hello Ada --greeting Hi --count 3 --shout

clitool tasks add "write docs" --tag dev --priority 1
clitool tasks list
clitool tasks list --all --json
clitool tasks done <id>
clitool tasks remove <id>

clitool config set user.name Ada
clitool config set user.age 36
clitool config get user.name
clitool config list
clitool config unset user.age
```

`python -m clitool ...` works as an alternative to the `clitool` script.

## Adding a command

Create `src/clitool/commands/mycmd.py` with a `register(subparsers)` function
that builds a parser and calls `parser.set_defaults(handler=run)`, then add
`mycmd.register` to `COMMANDS` in `src/clitool/commands/__init__.py`. Handlers
receive the parsed `argparse.Namespace` and may return an exit code or raise
`CliError` for a clean error message.

## Development

```bash
pytest        # run the test suite
ruff check .  # lint
ruff format . # format
```
