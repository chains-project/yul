# mylib

A pure-Python library that runs unmodified on Python 2.7 and Python 3.6+.

## Development

```sh
python -m venv .venv && . .venv/bin/activate
pip install -e ".[test]"
pytest
```

Run the full matrix (including Python 2.7) with tox:

```sh
pip install "tox<4" "virtualenv<20.22"
tox
```

## Python 2/3 compatibility conventions

- Every module starts with:

  ```python
  # -*- coding: utf-8 -*-
  from __future__ import absolute_import, division, print_function, unicode_literals
  ```

- Version-specific imports and type aliases (`text_type`, `binary_type`,
  `string_types`, `integer_types`, …) live in `mylib/_compat.py`. Don't check
  `sys.version_info` elsewhere — add a shim there instead.
- Be explicit about text vs. bytes: use `b"..."` for bytes literals and
  `mylib.to_text` / `mylib.to_bytes` at I/O boundaries.
- Use `io.open(..., encoding=...)` instead of the builtin `open` for text files.
- Avoid syntax unavailable in 2.7: f-strings, type annotations (use type
  comments), `async`/`await`, keyword-only arguments, `nonlocal`,
  `yield from`, and `print` without parentheses.
- Packaging uses `setup.py` (not a PEP 621 `pyproject.toml`) because the last
  pip/setuptools that support Python 2.7 can't read PEP 621 metadata. Wheels
  are built as universal (`py2.py3`).
