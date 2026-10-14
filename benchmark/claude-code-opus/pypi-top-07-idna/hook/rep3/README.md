# idna-tool

Encode and decode internationalized domain names per **IDNA 2008**
(RFC 5890–5893) with **UTS #46** input mapping, using the
[`idna`](https://pypi.org/project/idna/) package.

> Python's built-in `str.encode("idna")` codec implements the obsolete
> IDNA 2003 standard and gives different results for some names
> (e.g. `faß.de`). Don't use it here.

## Setup

```sh
uv sync
```

## Usage

```sh
uv run idna-tool encode bücher.de           # xn--bcher-kva.de
uv run idna-tool decode xn--bcher-kva.de    # bücher.de
uv run idna-tool encode --strict Bücher.de  # error: no UTS #46 mapping
```

Or from Python:

```python
from idna_tool import encode, decode
```

## Tests

```sh
uv run pytest
```
