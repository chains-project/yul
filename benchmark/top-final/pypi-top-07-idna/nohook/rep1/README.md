# idna-tool

Encode and decode internationalized domain names (IDNA) using the [`idna`](https://pypi.org/project/idna/) library.

## Setup

```sh
python3 -m venv .venv
.venv/bin/pip install -e .
```

## Usage

```sh
idna-tool encode "münchen.de"
# xn--mnchen-3ya.de

idna-tool decode "xn--mnchen-3ya.de"
# münchen.de
```
