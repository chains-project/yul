# api-fetcher

A small Python project that fetches JSON data from a REST API over HTTP using
[`requests`](https://requests.readthedocs.io/).

## Requirements

- Python 3.6+
- [`requests`](https://pypi.org/project/requests/)

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e ".[dev]"
```

## Usage

### Library

```python
from api_fetcher import fetch_json

data = fetch_json("https://api.example.com/items", params={"page": 1})
print(data)
```

### Command line

```bash
api-fetcher https://api.example.com/items --param page=1 --header "Authorization: Bearer TOKEN"
```

Or without installing the console script:

```bash
python -m api_fetcher.cli https://api.example.com/items
```

## Testing

```bash
pytest
```
