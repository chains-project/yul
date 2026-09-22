# http-client

A small Python project demonstrating low-level HTTP control with
[`urllib3`](https://urllib3.readthedocs.io/): explicit connection pooling,
timeouts and automatic retries.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

```bash
http-client https://httpbin.org/get --retries 5 --timeout 10
```

```python
from http_client import build_client

with build_client(max_connections=20, max_retries=3, backoff_factor=0.5) as client:
    response = client.get("https://httpbin.org/get")
    print(response.status, response.data)
```

### What it gives you

- **Connection pooling** via `urllib3.PoolManager` (`num_pools` / `maxsize`),
  so keep-alive connections are reused across requests.
- **Automatic retries** via `urllib3.Retry`, including connect/read/status
  retries, exponential backoff and `Retry-After` support.
- **Timeouts** split into separate connect and read values.
- **TLS verification** controlled through `cert_reqs`.
