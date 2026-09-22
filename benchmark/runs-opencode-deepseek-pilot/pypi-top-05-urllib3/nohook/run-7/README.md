# http-client

A small script for low-level HTTP control: connection pooling and automatic
retries via [`urllib3`](https://urllib3.readthedocs.io/).

## Setup

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
```

Or just install the dependency directly:

```bash
pip install "urllib3>=1.26,<3"
```

## Usage

```bash
python http_client.py https://httpbin.org/get
python http_client.py -X POST -d '{"a": 1}' https://httpbin.org/post
python http_client.py --retries 5 --maxsize 20 https://httpbin.org/get
```

As a library:

```python
from http_client import build_pool_manager, build_retry, request

http = build_pool_manager(maxsize=20, retries=build_retry(total=5))
status, body = request(http, "GET", "https://httpbin.org/get")
http.clear()
```

## What it configures

- **Connection pooling** — `PoolManager(num_pools, maxsize, block)` keeps a
  bounded pool of persistent connections per host and reuses them.
- **Automatic retries** — `Retry` retries connect/read/status failures with
  exponential backoff, honoring `Retry-After`. Retries cover
  `429, 500, 502, 503, 504`.
- **Timeouts** — separate connect and read timeouts.
- **TLS** — certificate verification required by default.
