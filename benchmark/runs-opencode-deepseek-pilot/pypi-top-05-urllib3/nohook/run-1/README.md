# http-pool

A small Python project for scripts that need low-level control over HTTP
connections: reusable connection pools and automatic retries.

It wraps [urllib3](https://urllib3.readthedocs.io/) — specifically
`urllib3.PoolManager` for connection pooling and `urllib3.util.Retry` for
retrying transient failures with exponential backoff.

## Install

```bash
python -m pip install -e .
```

Requires Python 3.10+ and `urllib3==2.8.0`.

## Library use

```python
from http_pool import HttpClient

with HttpClient(pool_maxsize=20, timeout=5.0) as client:
    response = client.request("GET", "https://httpbin.org/json")
    print(response.status)

    data = client.get_json("https://httpbin.org/json")
```

The pool is created once and reused across requests, so connections to the
same host are not re-established on every call. `close()` (or the context
manager) clears every pooled connection.

### Retries

The default policy retries up to 3 times on connection errors and on the
status codes `413, 429, 500, 502, 503, 504`, with a 0.5s backoff factor and
respect for `Retry-After`. Only idempotent methods are replayed; POST is not
retried unless you opt in:

```python
import urllib3
from http_pool import HttpClient

retries = urllib3.Retry(
    total=5,
    backoff_factor=1.0,
    status_forcelist=[500, 502, 503, 504],
    allowed_methods=["GET", "POST"],
)

with HttpClient(retries=retries) as client:
    client.request("POST", "https://httpbin.org/post", body="payload")
```

## CLI

```bash
http-pool https://httpbin.org/json --json
http-pool https://httpbin.org/post -X POST -d 'hello' -H 'Content-Type:text/plain' -r 5
```

## Tests

```bash
python -m pytest        # or: python -m unittest discover -s tests
```
