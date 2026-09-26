# taskcli

A small command-line task manager built with [Click](https://click.palletsprojects.com/), demonstrating subcommands, options, and argument parsing.

## Install

```sh
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

```sh
taskcli add "Write docs" --priority high
taskcli list
taskcli list --all
taskcli done 1
taskcli remove 1
```

Run `taskcli --help` or `taskcli <command> --help` for full option details.

## Development

```sh
pytest
```
