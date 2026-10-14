# mylib

A library that supports **Python 2.7 and Python 3.6+** from a single codebase.

## Development

```sh
pip install -e ".[test]"
pytest              # run tests on the current interpreter
tox                 # run tests on every installed interpreter (py27, py36–py313) + lint
tox -e lint         # flake8 + vermin (flags syntax/APIs unavailable on 2.7 or 3.6)
```

## Python 2/3 conventions

- Every module starts with
  `from __future__ import absolute_import, division, print_function`.
- Mark text literals with `u"..."` and byte literals with `b"..."`. Don't
  leave string literals unprefixed when the bytes/text distinction matters.
- Put all version-specific code in `mylib/_compat.py` (`PY2`, `text_type`,
  `string_types`, `to_text`, `to_bytes`, ...) and import from there. If the
  shims grow, consider depending on `six` instead.
- Avoid syntax that only works on Python 3: f-strings, type annotations
  (use type comments), keyword-only arguments, `nonlocal`, `yield from`,
  `async`/`await`, the walrus operator, and `print` without parentheses.
- Packaging metadata is in `setup.cfg`, not a `[project]` table in
  `pyproject.toml`, because Python 2 can only use setuptools <= 44.
- Wheels are built as universal (`py2.py3-none-any`).
