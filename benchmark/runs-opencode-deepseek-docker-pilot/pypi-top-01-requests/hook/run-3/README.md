# api-fetcher

Fetch data from a REST API over HTTP. Small Python library plus a command
line tool that GETs a URL and prints the decoded JSON.

## Requirements

- Python 3.9+

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Command line usage

```bash
api-fetcher https://api.example.com/users
api-fetcher https://api.example.com/search -p q=python -p limit=5
api-fetcher https://api.example.com/me -H "Authorization: Bearer $TOKEN"
```

`--param/-p` values become query parameters and `--header/-H` values are sent
as request headers.

## Library usage

```python
from api_fetcher import ApiClient

with ApiClient("https://api.example.com", headers={"X-Api-Key": "secret"}) as api:
    users = api.get("users", params={"limit": 10})
```

`ApiClient.get` raises `api_fetcher.ApiError` for connection failures, non-2xx
responses, and bodies that are not valid JSON. The client reuses a single
`requests.Session`, so pass one in if you want to share connection settings.

## Tests

```bash
pytest
```
