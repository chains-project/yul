# tabular

Load, clean, and analyze tabular data from CSV files. Pure Python standard library (3.10+), no dependencies.

```python
from tabular import load_csv

t = (
    load_csv("orders.csv")          # sniffs delimiter, strips BOM, infers types
    .clean_column_names()           # " Unit Price " -> "unit_price"
    .strip_whitespace()
    .drop_duplicates()
    .fill_missing(strategy="median", columns=["unit_price"])
    .drop_missing(["qty"])
)

t.describe()                        # per-column summary stats
t.value_counts("region")            # [("North", 2), ...]
t.correlation()                     # Pearson matrix over numeric columns
t.group_by("region", {"qty": ["sum", "mean"], "order_id": "count"})
print(t.to_string())
```

## Modules

| Module | Contents |
| --- | --- |
| `table.py` | `Table`: column-oriented container with `select`, `drop`, `rename`, `with_column`, `sort_by`, `head`, `rows()`; plus chainable wrappers for everything below |
| `loader.py` | `load_csv`, `read_csv_text`, `write_csv`. Infers `int`/`float`/`bool`/`date`/`datetime` per column; missing markers (`""`, `NA`, `N/A`, `null`, …) become `None` |
| `clean.py` | `clean_column_names`, `strip_whitespace`, `drop_duplicates`, `drop_missing`, `fill_missing` (constant, dict, or `mean`/`median`/`mode`/`ffill`/`bfill`), `cast_column`, `filter_rows` |
| `analysis.py` | `describe`, `value_counts`, `correlation`, `group_by` (built-in aggregations: `count`, `size`, `sum`, `mean`, `median`, `min`, `max`, `std`, `nunique`, `first`, or any callable) |

Every operation returns a new `Table`, so the original data is never modified.

## Tests

```
python3 -m unittest discover -s tests
```
