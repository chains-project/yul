# cert-check

A Python script that checks HTTPS connections against an up-to-date root CA bundle
from [certifi](https://pypi.org/project/certifi/), which packages Mozilla's curated trust store.
Because of this, verification doesn't depend on the host OS's certificate store.

## Usage

```sh
uv sync
uv run cert-check https://example.com
```

## Keeping the CA bundle current

New certifi releases follow Mozilla's root store updates. Refresh it from time to time:

```sh
uv lock --upgrade-package certifi && uv sync
```

To use the same bundle with other tools (e.g. `requests`, `httpx`), pass
`certifi.where()` as the CA file, or `cert_check.ssl_context()` as the SSL context.
