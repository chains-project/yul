# idna-tool

Encode and decode internationalized domain names per IDNA 2008 (RFC 5891)
with UTS #46 compatibility mapping, using the [`idna`](https://pypi.org/project/idna/) package.

> Python's built-in `str.encode("idna")` implements the obsolete IDNA 2003
> standard and gives different results for some names (e.g. `faß.de`), so it is
> deliberately not used.

## Usage

```sh
uv sync
uv run idna-tool encode münchen.de         # xn--mnchen-3ya.de
uv run idna-tool decode xn--mnchen-3ya.de  # münchen.de
uv run pytest
```
