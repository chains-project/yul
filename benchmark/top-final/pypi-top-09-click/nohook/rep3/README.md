# taskcli

A small command-line task manager built with [Click](https://click.palletsprojects.com/), used as an example of a multi-command CLI with options and argument parsing.

## Install

```sh
pip install -e ".[dev]"
```

## Usage

```sh
task add "Write report" --priority high --tag work
task add "Buy milk"
task list                      # pending tasks only
task list --all                # include completed
task list --tag work --priority high
task done 1
task remove 2 --yes
```

Tasks are stored in `~/.taskcli/tasks.json` by default; override with `--tasks-file` or the `TASKCLI_FILE` env var.

## Develop

```sh
pytest
```
