# mytool

A command-line tool with multiple subcommands, options, and argument parsing,
built on the Python standard library (`argparse`).

## Installation

```console
python -m pip install -e ".[dev]"
```

## Usage

```console
mytool --help
mytool --version
mytool greet --name Ada --count 2 --shout
mytool config show
mytool config set greeting "Hello there"
```

Every subcommand accepts `--help`, e.g. `mytool greet --help`.

## Development

Run the test suite:

```console
python -m pytest
```

## Layout

```
src/mytool/          Package source (src layout)
  cli.py             Argument parser and dispatch
  commands/          One module per subcommand
tests/               Pytest suite
```
