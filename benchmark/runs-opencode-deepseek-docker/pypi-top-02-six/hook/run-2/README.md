# compatlib

A small example library whose source code is written to be importable and
testable on **both Python 2.7 and Python 3**.

> Python 2.7 is end-of-life. This layout exists for libraries that still need
> to support legacy interpreters; new projects should target Python 3 only.

## Layout

```
compatlib/            importable package
    __init__.py       public API + version
    _compat.py        Python 2/3 compatibility shims
    core.py           example implementation
tests/                unittest suite (stdlib only, runs on 2.7)
setup.py / setup.cfg  packaging metadata
tox.ini               runs the tests under each supported interpreter
```

## Installation

```console
$ pip install -e .
```

## Usage

```python
from compatlib import greet, read_text

greet("World")            # -> "Hello, World!"
greet(b"World")           # accepts bytes on both majors
read_text("notes.txt")    # returns text, decoded as UTF-8
```

## Writing 2/3-compatible source

The rules the code in this project follows:

1. Start every module with the `__future__` imports:
   ```python
   from __future__ import absolute_import, division, print_function, unicode_literals
   ```
2. Import compatibility helpers from `compatlib._compat` instead of branching
   on `sys.version_info` at each call site.
3. Use `io.open(path, encoding=...)` for text I/O; the builtin `open` on
   Python 2 returns bytes.
4. Avoid Python 3-only syntax: no f-strings, no keyword-only arguments, no
   `nonlocal`, and no `yield from`.

## Testing

Run the suite under the current interpreter:

```console
$ python -m unittest discover -s tests -t . -v
```

Run it under every supported interpreter with [tox](https://tox.wiki/):

```console
$ tox
```

## License

MIT. See [LICENSE](LICENSE).
