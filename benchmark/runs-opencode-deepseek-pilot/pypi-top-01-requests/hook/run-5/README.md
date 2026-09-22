# rest-api-fetch

A small Python script that fetches JSON data from a REST API over HTTP.

## Setup

```sh
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Usage

```sh
python fetch_data.py https://jsonplaceholder.typicode.com/todos/1
python fetch_data.py https://api.example.com/items --timeout 5 -o items.json
```

`fetch_data.py` performs a `GET` request, raises on non-2xx responses, and
prints the JSON body (pretty-printed) or writes it to the file given with
`--output`.
