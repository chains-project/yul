# api-fetcher

A small Python script/library that fetches data from a REST API over HTTP.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

## Usage

As a library:

```python
from api_fetcher import ApiClient

with ApiClient("https://api.example.com", headers={"Accept": "application/json"}) as client:
    data = client.get("/users", params={"page": 1})
    print(data)
```

As a command line tool:

```bash
api-fetcher https://api.example.com -p /users -q page=1 -H "Authorization: Bearer TOKEN"
```

Or without installing the entry point:

```bash
python -m api_fetcher.cli https://api.example.com -p /users
```

## Tests

```bash
python -m pytest
```
