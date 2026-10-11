# secure-fetch

Fetch HTTPS resources with a reliable, up-to-date bundle of root SSL/TLS
certificates.

Trust is anchored on [certifi](https://github.com/certifi/python-certifi),
which ships Mozilla's curated CA store and publishes updates as new roots are
added or compromised roots are removed. Because the bundle is pinned to the
`certifi` package rather than the host operating system, behavior is consistent
across platforms and CI environments.

## Install

```sh
python -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

As a library:

```python
from secure_fetch import fetch

body = fetch("https://example.com")
```

As a command:

```sh
secure-fetch https://example.com
secure-fetch --show-ca-bundle   # path to the active CA bundle
```

## Development

```sh
pytest
```
