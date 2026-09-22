# api-fetcher

Fetch JSON data from a REST API over HTTP.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pip install -e .
```

## Usage

As a library:

```python
from api_fetcher import RestClient

with RestClient("https://api.example.com", timeout=10, retries=3) as client:
    data = client.get_json("/users", params={"page": 1})
    print(data)
```

From the command line:

```bash
api-fetcher https://api.example.com/users -p page=1 -H "Accept: application/json"
python3 -m api_fetcher https://api.example.com/users --param page=1
```

## Tests

```bash
pytest
```
