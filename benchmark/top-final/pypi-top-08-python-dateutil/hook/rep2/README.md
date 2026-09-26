# date-arith

Parse human-written date strings and compute relative date arithmetic using `python-dateutil`.

## Setup

```sh
python3 -m venv .venv
.venv/bin/pip install -e .
```

## Usage

Parse a flexible date string:

```sh
.venv/bin/python date_arith.py parse "March 3rd 2025"
```

Compute the first given weekday of next month:

```sh
.venv/bin/python date_arith.py first-weekday-next-month monday
```
