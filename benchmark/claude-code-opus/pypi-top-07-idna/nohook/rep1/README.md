# idna-tool

Encode and decode internationalized domain names per IDNA 2008 (RFC 5891)
with UTS #46 compatibility processing, built on the [`idna`](https://pypi.org/project/idna/) package.

> Python's built-in `str.encode("idna")` codec implements the obsolete IDNA 2003
> and gives different results (e.g. `ß`), so this project doesn't use it.

## Usage

```sh
uv sync
uv run idna-tool encode bücher.de        # xn--bcher-kva.de
uv run idna-tool decode xn--bcher-kva.de # bücher.de
uv run pytest
```

Library use:

```python
from idna_tool import encode, decode
encode("münchen.de")  # 'xn--mnchen-3ya.de'
```
