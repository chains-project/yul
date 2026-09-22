# REST API Fetcher

A small Python script that fetches JSON data from a REST API over HTTP.

## Setup

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```sh
python fetch_data.py https://api.example.com/items
python fetch_data.py https://api.example.com/items -p limit=10 -p page=2
```

The decoded JSON response is printed to stdout.
