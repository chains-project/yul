# mylib

A pure-Python library that runs unmodified on Python 2.7 and Python 3.6+.

## Development

```sh
pip install -e ".[test]"
pytest
tox            # run the full 2.7 / 3.x matrix
```

## Writing 2/3-compatible code

- Start every module with
  `from __future__ import absolute_import, division, print_function, unicode_literals`.
- Put all version-specific logic in `mylib/_compat.py`. Import names like
  `text_type`, `string_types` and `ensure_text` from there instead of
  checking `sys.version_info` elsewhere.
- Be explicit about bytes vs. text at API boundaries (`ensure_text` /
  `ensure_binary`).
- Avoid Python-3-only syntax: f-strings, annotations (use type comments),
  `nonlocal`, keyword-only arguments, `yield from`, `async`/`await`.
