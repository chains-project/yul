# clitool

A small command-line task tracker demonstrating a multi-command `argparse` CLI.
No third-party runtime dependencies.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Or run it straight from a checkout without installing:

```bash
PYTHONPATH=src python -m clitool --help
```

## Usage

```bash
clitool --help
clitool add "Write the report" --priority high --tag work
clitool list
clitool list --all --sort priority
clitool done 1
clitool remove 1
```

Global options:

- `--version` — print the version and exit.
- `-v`, `--verbose` — increase logging verbosity (repeatable).
- `--data-file PATH` — task store location. Defaults to
  `$CLITOOL_DATA_FILE` or `~/.clitool/tasks.json`.

Run `clitool COMMAND --help` for per-command options.

## Development

```bash
python -m unittest discover -s tests -v
# or, if pytest is installed
pytest
```
