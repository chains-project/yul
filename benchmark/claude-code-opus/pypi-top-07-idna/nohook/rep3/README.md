# idna-tool

Encode and decode internationalized domain names per IDNA 2008 (RFC 5891)
with UTS #46 compatibility mapping, using the [`idna`](https://pypi.org/project/idna/) package.

> Python's built-in `"idna"` codec implements the obsolete IDNA 2003 and
> gives different results for some names (e.g. `faß.de`). Don't use it.

## Setup

```sh
uv sync
```

## Usage

```sh
uv run idna-tool encode bücher.example     # xn--bcher-kva.example
uv run idna-tool decode xn--bcher-kva.example  # bücher.example
```

```python
from idna_tool import encode, decode
encode("münchen.de")  # 'xn--mnchen-3ya.de'
```

## Tests

```sh
uv run pytest
```
