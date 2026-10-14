# certcheck

Verifies HTTPS connections using [certifi](https://pypi.org/project/certifi/),
Mozilla's curated root CA bundle, instead of relying on the OS trust store.

## Usage

```sh
uv sync
uv run certcheck example.com
```

## Keeping the CA bundle current

certifi publishes new releases as Mozilla updates its root store. Refresh with:

```sh
uv lock --upgrade-package certifi && uv sync
```
