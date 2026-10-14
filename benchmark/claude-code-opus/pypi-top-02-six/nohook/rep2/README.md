# mylib

A library that supports both Python 2.7 and Python 3.6+ from one source tree.

## Development

```sh
pip install -e .[test]
pytest              # current interpreter
tox                 # every interpreter installed locally
```

## Writing Python 2/3 compatible code

- Start every module with
  `from __future__ import absolute_import, division, print_function, unicode_literals`.
- Put version-specific code in `mylib/_compat.py` and import from there
  instead of checking `sys.version_info` throughout the code.
- Don't use syntax that only exists in Python 3: f-strings, type annotations
  (use type comments), `async`/`await`, keyword-only arguments, `nonlocal`,
  `yield from`, or `print` without parentheses.
- Keep text and bytes apart: decode at I/O boundaries with `ensure_text`.
- Use `io.open(..., encoding=...)` instead of the builtin `open` for text files.

Packaging uses `setup.cfg` with a stub `setup.py`, because setuptools 44
(the last version that supports Python 2) can't read metadata from
`pyproject.toml`. `python setup.py bdist_wheel` (or `python -m build`)
produces a single universal `py2.py3` wheel.
