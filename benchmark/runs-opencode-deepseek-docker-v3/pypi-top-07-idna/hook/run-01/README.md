# idn-tool

Encode and decode internationalized domain names (IDNs) per IDNA 2008
(RFC 5890-5892), with optional UTS #46 compatibility processing.

## Setup

```sh
uv sync
```

## Usage

### CLI

Encode a Unicode domain to its ASCII (A-label) form:

```sh
uv run idn-tool encode münchen.de
# xn--mnchen-3ya.de

uv run idn-tool encode 例え.テスト
# xn--r8jz45g.xn--zckzah
```

Decode an A-label back to Unicode:

```sh
uv run idn-tool decode xn--mnchen-3ya.de
# münchen.de
```

Use `--uts46` to apply UTS #46 case folding and compatibility mapping, and
`--std3-rules` to enforce the STD3 ASCII rules:

```sh
uv run idn-tool encode --uts46 Bücher.example
# xn--bcher-kva.example
```

### Library

```python
from idn_tool import decode, encode

encode("münchen.de")  # 'xn--mnchen-3ya.de'
decode("xn--mnchen-3ya.de")  # 'münchen.de'
encode("Bücher.example", uts46=True)  # 'xn--bcher-kva.example'
```

Invalid input raises `idn_tool.IDNError`.

## Development

```sh
uv run pytest
uv run ruff check .
uv run ruff format .
```
