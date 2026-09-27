# api-fetcher

A small Python project for fetching data from a REST API over HTTP.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

Command line:

```bash
api-fetcher https://api.example.com/items
```

Or from Python:

```python
from api_fetcher import ApiClient

client = ApiClient("https://api.example.com", token="...")
items = client.get("/items", params={"limit": 10})
```

## Configuration

Create a `.env` file (see `.env.example`) or export environment variables:

- `API_BASE_URL` - base URL for the API
- `API_TOKEN` - bearer token used for authentication

## Tests

```bash
pytest
```
