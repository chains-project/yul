# mylib

A Python library that runs on both Python 2 and Python 3.

## Compatibility approach

- `from __future__ import absolute_import, division, print_function` at the
  top of every module.
- [`six`](https://six.readthedocs.io/) for the handful of APIs that differ
  between Python 2 and 3 (string types, `six.moves`, etc).
- No f-strings, `pathlib`, keyword-only arguments, or other Python
  3-only syntax in library code.

## Development

```sh
pip install -e .
pip install pytest
pytest tests

# or, to test against both interpreters:
tox
```

## Supported versions

Python 2.7 and Python 3.4+.
