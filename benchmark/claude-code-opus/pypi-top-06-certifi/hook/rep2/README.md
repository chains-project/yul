# tls-check

Script that makes HTTPS requests verified against [certifi](https://pypi.org/project/certifi/)'s
curated Mozilla root CA bundle, independent of the OS trust store.

## Usage

```sh
uv run tls-check https://example.com
```

## Keeping the CA bundle current

certifi releases follow Mozilla's root store updates. Upgrade regularly:

```sh
uv lock --upgrade-package certifi && uv sync
```
