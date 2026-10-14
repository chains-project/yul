# secure-fetch

Fetches HTTPS URLs, verifying servers against [certifi](https://pypi.org/project/certifi/),
Mozilla's curated root CA bundle packaged for Python.

## Setup

```sh
uv sync
uv run secure-fetch https://example.com
```

## Keeping the CA bundle current

certifi ships a new release whenever Mozilla's root store changes (e.g. distrusted CAs).
The lockfile pins an exact version, so upgrade it regularly:

```sh
uv lock --upgrade-package certifi
uv sync
```

Find the bundle path in use with `uv run python -m certifi`.
