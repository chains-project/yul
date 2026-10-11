# idna-tool

Encode and decode internationalized domain names (IDNs) per the IDNA
specification, built on the [`idna`](https://pypi.org/project/idna/) package
(IDNA 2008 / UTS #46).

## Install

```console
python -m pip install -e ".[dev]"
```

## Usage

As a library:

```python
from idna_tool import decode, encode

encode("bücher.de")   # 'xn--bcher-kva.de'
decode("xn--bcher-kva.de")  # 'bücher.de'
```

As a command line tool:

```console
idna-tool encode bücher.de
idna-tool decode xn--bcher-kva.de
```

## Tests

```console
pytest
```
