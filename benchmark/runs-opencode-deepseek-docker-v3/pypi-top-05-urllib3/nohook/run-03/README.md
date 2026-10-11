# httpkit

A small, explicit HTTP client for scripts that need low-level control over
connections. Built directly on [urllib3](https://urllib3.readthedocs.io/).

- Connection pooling (`maxsize`, `num_pools`, blocking behavior)
- Tunable automatic retries (backoff, status list, allowed methods)
- Per-request timeouts, streaming, and raw `HTTPResponse` access
- HTTPS verification via `certifi`, optional proxy support

## Install

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

```python
from httpkit import HTTPClient, RetryPolicy

policy = RetryPolicy(
    total=5,
    backoff_factor=0.5,
    status_forcelist=(429, 500, 502, 503, 504),
)

with HTTPClient(timeout=30.0, retries=policy, maxsize=20) as client:
    response = client.get("https://example.com/api", preload_content=True)
    print(response.status, response.data)

    # stream a large body without buffering it in memory
    for chunk in client.stream("GET", "https://example.com/big"):
        ...
```

### CLI

```bash
httpkit https://example.com -X GET -H "Accept: application/json" --retries 5
httpkit https://example.com/file --stream > file.bin
```

## Tests

```bash
pytest
```
