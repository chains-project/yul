# api-fetcher

A small Python script that fetches data from a REST API over HTTP.

## Features

- Simple `fetch` / `fetch_json` helpers built on [`requests`](https://requests.readthedocs.io/).
- Automatic retries with exponential backoff on transient errors (429/5xx).
- Sensible default timeout.
- Command-line interface for one-off requests.

## Install

```bash
uv sync
```

Or with pip:

```bash
pip install .
```

## Usage

Command line:

```bash
api-fetcher https://api.example.com/items
api-fetcher https://api.example.com/items -p q=widget -p page=2 -H Accept=application/json
api-fetcher https://api.example.com/items -t 10 -o items.json
```

As a library:

```python
from api_fetcher import fetch_json

data = fetch_json("https://api.example.com/items", params={"q": "widget"})
print(data)
```

## Development

```bash
uv run pytest
```
