# mytool

A command-line tool with multiple subcommands, options, and argument parsing.

## Layout

```
.
├── pyproject.toml            # packaging + entry point + tooling config
├── src/mytool/
│   ├── __init__.py           # version
│   ├── __main__.py           # `python -m mytool`
│   ├── cli.py                # top-level parser + dispatch
│   └── commands/             # one module per subcommand
│       ├── greet.py
│       ├── files.py
│       └── config.py
└── tests/
    └── test_cli.py
```

Adding a subcommand means creating a module in `src/mytool/commands/` with a
`register(subparsers)` function and a `run(args) -> int` handler, then calling
its `register` from `build_parser()` in `cli.py`. The handler's return value
becomes the process exit code.

## Development

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

```bash
mytool --help
mytool greet Ada --count 2 --shout
mytool files . --all -e .py
mytool config set color blue
mytool config get color
mytool config show
```

Run it without installing with `PYTHONPATH=src python -m mytool`.

## Tests

```bash
pytest            # or: python -m unittest discover -s tests
```
