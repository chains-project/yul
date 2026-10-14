# idna-tool

Encode and decode internationalized domain names per IDNA 2008 (RFC 5891),
with UTS #46 mapping by default.

Built on the [`idna`](https://pypi.org/project/idna/) package. Python's built-in
`"idna"` codec is **not** used because it only implements the older IDNA 2003.

## Usage

```sh
uv run idna-tool encode bücher.de        # xn--bcher-kva.de
uv run idna-tool decode xn--bcher-kva.de # bücher.de
uv run idna-tool encode --strict ...     # skip UTS #46 normalization
```

## Development

```sh
uv run pytest
```
