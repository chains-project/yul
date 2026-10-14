# mylib

A library that supports Python 2.7 and Python 3.6+ from a single codebase.

## Development

```sh
pip install -e .[test]
pytest
tox            # run against every installed interpreter
```

## Python 2/3 compatibility rules

- Start every module with
  `from __future__ import absolute_import, division, print_function, unicode_literals`
  and a `# -*- coding: utf-8 -*-` header.
- Put all version-specific code in `mylib/_compat.py`; import names from there
  instead of checking `sys.version_info` elsewhere.
- Be explicit about bytes vs. text at API boundaries (`to_text` / `to_bytes`).
- Don't use Python 3-only syntax: f-strings, type annotations (use type
  comments), `print` without parentheses, `nonlocal`, keyword-only arguments,
  `yield from`, `async`/`await`, the walrus operator.
- Classes should inherit from `object` explicitly.
- Packaging: metadata is in `setup.cfg` (not `[project]` in `pyproject.toml`,
  which Python 2 setuptools cannot read). A universal `py2.py3` wheel is built.
