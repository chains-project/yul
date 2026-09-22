# rest-fetcher

A small Python project for fetching JSON data from a REST API over HTTP.

## Requirements

- Python 3.9+

## Setup

Using [uv](https://docs.astral.sh/uv/):

```bash
uv sync --extra dev
```

Or plain pip in a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

As a command-line script:

```bash
rest-fetcher https://api.example.com/items
rest-fetcher https://api.example.com/search -p q=python -p page=2
rest-fetcher https://api.example.com/me -H "Authorization: Bearer TOKEN"
rest-fetcher https://api.example.com/items --compact -o items.json
```

As a library:

```python
from rest_fetcher import RestClient, fetch

data = fetch("https://api.example.com/items")

with RestClient(
    base_url="https://api.example.com",
    headers={"Authorization": "Bearer TOKEN"},
) as client:
    items = client.get("/items", params={"page": 2})
```

## Development

```bash
uv run pytest
```
