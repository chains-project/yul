# notemgr

A small command-line note manager built with [Click](https://click.palletsprojects.com/), demonstrating subcommands, options, and argument parsing.

## Install

```sh
pip install -e .
```

## Usage

```sh
notemgr add "Buy milk" --tag errand
notemgr add "Finish report" -t work -t urgent
notemgr list
notemgr list --tag work
notemgr done 1
notemgr remove 1
```

Notes are stored in `~/.notemgr/notes.json` by default; override with `--store PATH`.
