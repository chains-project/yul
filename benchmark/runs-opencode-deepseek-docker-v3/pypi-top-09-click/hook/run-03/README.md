# mytool

A small, dependency-free command-line tool built on Python's standard
[`argparse`](https://docs.python.org/3/library/argparse.html). It demonstrates a
conventional CLI layout with multiple subcommands, optional/positional
arguments, type conversion, and nested subcommands.

## Installation

```bash
# Editable install with development dependencies
python -m pip install -e ".[dev]"
```

## Usage

```bash
mytool --help
mytool greet Ada --count 2 --uppercase
mytool calc add 2 3 4
mytool wordcount README.md
```

### Commands

| Command | Description |
| --- | --- |
| `greet` | Greet someone (positional, `--greeting`, `--count`, `--uppercase`). |
| `calc` | Arithmetic with nested subcommands: `add`, `subtract`, `multiply`. |
| `wordcount` | Count lines, words, and characters in files (or stdin). |

## Development

```bash
python -m pytest          # run tests
ruff check .              # lint
ruff format .             # format
```

## Project layout

```
src/mytool/
    __init__.py
    __main__.py        # enables `python -m mytool`
    cli.py             # top-level parser + dispatch
    commands/
        greet.py
        calc.py
        wordcount.py
tests/
    test_cli.py
```
