# taskcli

A small command-line task manager built with [Click](https://click.palletsprojects.com/), demonstrating subcommands, options, and argument parsing.

## Install

```sh
pip install -e .
```

## Usage

```sh
taskcli add "Write the report" --priority high
taskcli list
taskcli list --all
taskcli done 1
taskcli remove 1
```

Use `--store PATH` (before the subcommand) to point at a different tasks file, and `--help` on any command for details.
