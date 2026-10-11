# idn-tools

Encode and decode internationalized domain names (IDNs) according to
**IDNA 2008** (RFC 5890/5891/5892) and **UTS #46**, built on the
[`idna`](https://pypi.org/project/idna/) package.

The Python standard library's `str.encode("idna")` codec implements the
obsolete IDNA 2003 rules. This project uses the modern `idna` package
instead, so mappings such as `ß` are handled correctly.

## Install

```sh
uv sync          # or: pip install -e .
```

## Library usage

```python
from idn_tools import encode_domain, decode_domain

encode_domain("münchen.de")            # 'xn--mnchen-3ya.de'
encode_domain("BÜCHER.de")             # 'xn--bcher-kva.de'  (case folding)
decode_domain("xn--mnchen-3ya.de")     # 'münchen.de'

encode_domain("faß.de")                # 'xn--fa-hia.de'     (IDNA 2008)
```

All encoding/decoding failures raise `idn_tools.IDNAError`.

## Command line usage

```sh
idn encode münchen.de bücher.example
# xn--mnchen-3ya.de
# xn--bcher-kva.example

idn decode xn--mnchen-3ya.de
# münchen.de

idn --no-uts46 encode example.com   # strict IDNA 2008, no UTS #46 mapping
```

## Development

```sh
uv run pytest
```
