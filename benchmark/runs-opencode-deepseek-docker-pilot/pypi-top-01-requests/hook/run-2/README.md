# api-fetch

A small Python script that fetches JSON from a REST API over HTTP.

## Setup

Managed with [uv](https://docs.astral.sh/uv/). Dependencies are locked in
`uv.lock`.

```bash
uv sync
```

## Usage

```bash
api-fetch /users --base-url https://api.example.com
# or
API_BASE_URL=https://api.example.com python -m api_fetch /users -p page=2
```

Query parameters can be repeated with `-p/--param`. The response is printed as
indented JSON on stdout; non-2xx responses exit with status `1`.

## Library use

```python
from api_fetch import ApiClient

client = ApiClient("https://api.example.com", timeout=5.0)
data = client.get("/users", params={"page": 2})
```

## Tests

```bash
uv run pytest
```
