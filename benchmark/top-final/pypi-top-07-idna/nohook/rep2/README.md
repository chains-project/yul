# idna-tool

Encode and decode internationalized domain names (IDNA) using the [`idna`](https://pypi.org/project/idna/) package.

## Setup

```sh
python3 -m venv .venv
.venv/bin/pip install -e .
```

## Usage

```sh
.venv/bin/python idna_tool.py encode "münchen.de"
# xn--mnchen-3ya.de

.venv/bin/python idna_tool.py decode "xn--mnchen-3ya.de"
# münchen.de
```
