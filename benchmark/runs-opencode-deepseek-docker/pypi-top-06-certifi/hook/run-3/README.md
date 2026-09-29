# secure-fetch

Fetch URLs over HTTPS with certificate verification against
[certifi](https://github.com/certifi/python-certifi)'s curated, up-to-date
copy of Mozilla's root CA bundle.

`certifi` is used directly (rather than the interpreter's system trust store)
so verification works reliably across platforms and stays current through
normal dependency updates.

## Usage

```bash
pip install -e .
secure-fetch https://example.com
secure-fetch https://example.com -o page.html
```

## Library

```python
from secure_fetch import fetch

body = fetch("https://example.com")
```

Use `build_ssl_context()` if you need the configured `ssl.SSLContext` for
other clients.

## Development

```bash
pip install -e ".[dev]"
pytest
```

Keep the trust bundle current with `pip install --upgrade certifi`.
