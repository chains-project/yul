# https-cert-check

Verifies HTTPS connections against Mozilla's root CA bundle, kept current via [certifi](https://pypi.org/project/certifi/).

## Setup

```sh
python3 -m venv .venv
.venv/bin/pip install -e .
```

## Usage

```sh
.venv/bin/python check_https.py https://example.com
```
