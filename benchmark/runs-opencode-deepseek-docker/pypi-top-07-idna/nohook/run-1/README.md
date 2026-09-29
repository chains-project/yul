# idna-tool

Encode and decode internationalized domain names (IDNs) according to
[IDNA 2008](https://www.rfc-editor.org/rfc/rfc5890) (RFC 5890/5891) with
[UTS #46](https://www.unicode.org/reports/tr46/) processing.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

As a library:

```python
from idna_tool import decode, encode

encode("Bücher.example")        # 'xn--bcher-kva.example'
decode("xn--bcher-kva.example") # 'bücher.example'
```

From the command line:

```bash
idna-tool encode "Bücher.example"        # xn--bcher-kva.example
idna-tool decode "xn--bcher-kva.example" # bücher.example
```

## Test

```bash
pytest
```

## Note on the standard library

The `encodings.idna` codec bundled with CPython implements the obsolete
IDNA 2003 behaviour and is not safe for general use. This project depends on
the `idna` package, which tracks the current specification.
