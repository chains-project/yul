# idna-toolkit

Encode and decode internationalized domain names (IDNs) following IDNA2008
(RFC 5890-5895), with optional UTS #46 processing.

Backed by the reference [`idna`](https://pypi.org/project/idna/) package.

## Install

```console
python -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
```

## Library usage

```python
from idna_toolkit import encode, decode, is_idn

encode("例え.テスト")            # 'xn--r8jz45g.xn--zckzah'
decode("xn--r8jz45g.xn--zckzah") # '例え.テスト'
encode("BÜCHER.example", uts46=True)  # 'xn--bcher-kva.example'
is_idn("xn--bcher-kva.example")       # True
```

Single labels are available through `encode_label` / `decode_label`.

Invalid input raises `idna_toolkit.IDNAError` (a subclass of `ValueError`).

## Command line usage

```console
$ idna-toolkit encode 例え.テスト münchen.de
xn--r8jz45g.xn--zckzah
xn--mnchen-3ya.de

$ idna-toolkit decode xn--r8jz45g.xn--zckzah
例え.テスト

$ printf 'BÜCHER.example\n' | idna-toolkit encode --uts46
xn--bcher-kva.example
```

Both subcommands accept `--uts46`; `encode` additionally accepts
`--transitional` and `decode` accepts `--display`.

## Tests

```console
pytest
```
