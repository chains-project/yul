# mycli

A sample command-line tool built with [Click](https://click.palletsprojects.com/), demonstrating subcommands, options, and argument parsing.

## Install

```sh
pip install -e ".[dev]"
```

## Usage

```sh
mycli --help
mycli greet World --count 3
mycli config set key value
mycli config get key
```

## Test

```sh
pytest
```
