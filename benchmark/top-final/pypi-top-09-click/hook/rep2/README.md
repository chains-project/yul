# taskcli

A small command-line task manager built with [Click](https://click.palletsprojects.com/), showing subcommands, options, and argument parsing.

## Install

```sh
uv sync
```

## Usage

```sh
uv run taskcli add "Buy milk" --priority high
uv run taskcli list
uv run taskcli list --all
uv run taskcli done 1
uv run taskcli remove 1
```

Tasks are stored as JSON at `~/.taskcli/tasks.json` by default; override with `--store PATH` (before the subcommand).

## Development

```sh
uv sync --extra dev
uv run pytest
```
