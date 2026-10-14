# idnconv

Encode and decode internationalized domain names per **IDNA 2008**
(RFC 5891) with **UTS #46** mapping, using the [`idna`](https://pypi.org/project/idna/) package.

> Python's built-in `str.encode("idna")` implements the obsolete IDNA 2003
> standard and gives different results (e.g. `straße.de` → `strasse.de`), so
> it is deliberately not used.

## Usage

```sh
uv run idnconv encode bücher.de        # xn--bcher-kva.de
uv run idnconv decode xn--bcher-kva.de # bücher.de
uv run idnconv encode --strict ...     # skip UTS #46 normalization
```

As a library:

```python
from idnconv import encode, decode, IDNAError
```

## Development

```sh
uv sync
uv run pytest
```
