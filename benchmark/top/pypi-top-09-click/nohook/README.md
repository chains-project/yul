# taskcli

A command-line task manager built with [click](https://click.palletsprojects.com/), demonstrating subcommands, options, and argument parsing.

## Install

```sh
pip install -e .
```

## Usage

```sh
taskcli add "Buy milk" --priority high
taskcli list
taskcli list --all
taskcli done 1
taskcli remove 1
```

Global options:

- `-f, --file PATH` — use a custom task storage file (default `~/.taskcli.json`)
- `-v, --verbose` — verbose output

## Development

```sh
pip install -e ".[dev]"
pytest
```
