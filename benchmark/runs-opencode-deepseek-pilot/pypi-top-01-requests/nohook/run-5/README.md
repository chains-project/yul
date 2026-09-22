# api-fetcher

A small Python project for fetching data from a REST API over HTTP.

It uses [`requests`](https://requests.readthedocs.io/) under the hood and ships
both an importable helper and a command line script.

## Requirements

- Python 3.8+

## Setup

Using [uv](https://docs.astral.sh/uv/):

```bash
uv sync
```

Or with a plain virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Usage

Command line:

```bash
api-fetcher https://api.github.com/repos/psf/requests
api-fetcher https://httpbin.org/get -p page=2 -p per_page=10 -H "Accept: application/json"
```

Library:

```python
from api_fetcher import fetch_json

data = fetch_json("https://api.github.com/repos/psf/requests")
print(data["full_name"])
```

## Development

```bash
uv run pytest
```
