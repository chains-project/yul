# secure-fetch

Fetches HTTPS URLs, verifying servers against the
[certifi](https://pypi.org/project/certifi/) root CA bundle (Mozilla's curated
trust store) instead of whatever the OS happens to ship.

## Setup

```sh
uv sync            # or: python -m venv .venv && .venv/bin/pip install -e .
```

## Usage

```sh
uv run secure-fetch https://example.com
```

## Keeping the CA bundle current

certifi releases a new version whenever Mozilla's root store changes. Upgrade
regularly:

```sh
uv lock --upgrade-package certifi && uv sync
```

Path to the bundle in use: `uv run python -m certifi`
