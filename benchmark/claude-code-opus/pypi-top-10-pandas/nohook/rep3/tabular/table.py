"""The :class:`Table` container. Operations return new tables."""

from __future__ import annotations

import csv
import os
from typing import Any, Callable, Iterable, Iterator, Mapping

from . import analysis
from .cleaning import convert_column, infer_type, is_missing, normalize_name


class Table:
    """A column-oriented table: an ordered mapping of name -> list of values."""

    def __init__(self, columns: Mapping[str, Iterable[Any]]):
        self._cols = {name: list(values) for name, values in columns.items()}
        lengths = {len(v) for v in self._cols.values()}
        if len(lengths) > 1:
            raise ValueError(f"columns have different lengths: {sorted(lengths)}")

    @classmethod
    def from_rows(cls, rows: Iterable[Mapping[str, Any]]) -> "Table":
        """Build a table from dicts; keys missing from a row become ``None``."""
        rows = list(rows)
        names: dict[str, None] = {}
        for row in rows:
            names.update(dict.fromkeys(row))
        return cls({n: [row.get(n) for row in rows] for n in names})

    # -- basic access --------------------------------------------------------

    @property
    def columns(self) -> list[str]:
        return list(self._cols)

    @property
    def shape(self) -> tuple[int, int]:
        return len(self), len(self._cols)

    def __len__(self) -> int:
        return len(next(iter(self._cols.values()), []))

    def __getitem__(self, name: str) -> list:
        return list(self._cols[name])

    def __contains__(self, name: str) -> bool:
        return name in self._cols

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Table) and self._cols == other._cols

    def rows(self) -> Iterator[dict[str, Any]]:
        names = self.columns
        for values in zip(*self._cols.values()):
            yield dict(zip(names, values))

    def to_dicts(self) -> list[dict[str, Any]]:
        return list(self.rows())

    def dtypes(self) -> dict[str, str]:
        """Inferred type name of each column (see :func:`infer_type`)."""
        return {n: analysis.column_type(v) for n, v in self._cols.items()}

    def __repr__(self) -> str:
        return f"Table({len(self)} rows x {len(self._cols)} columns: {self.columns})"

    def __str__(self) -> str:
        return self.to_string()

    def to_string(self, max_rows: int = 20) -> str:
        names = self.columns
        body = [["" if v is None else str(v) for v in row.values()]
                for _, row in zip(range(max_rows), self.rows())]
        widths = [max([len(n)] + [len(r[i]) for r in body]) for i, n in enumerate(names)]
        lines = ["  ".join(n.ljust(w) for n, w in zip(names, widths))]
        lines.append("  ".join("-" * w for w in widths))
        lines += ["  ".join(c.ljust(w) for c, w in zip(r, widths)) for r in body]
        if len(self) > max_rows:
            lines.append(f"... ({len(self) - max_rows} more rows)")
        return "\n".join(lines)

    def to_csv(self, path: str | os.PathLike, *, delimiter: str = ",") -> None:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=delimiter)
            writer.writerow(self.columns)
            for values in zip(*self._cols.values()):
                writer.writerow("" if v is None else v for v in values)

    # -- selection -----------------------------------------------------------

    def _take(self, indices: Iterable[int]) -> "Table":
        indices = list(indices)
        return Table({n: [v[i] for i in indices] for n, v in self._cols.items()})

    def head(self, n: int = 5) -> "Table":
        return self._take(range(min(n, len(self))))

    def tail(self, n: int = 5) -> "Table":
        return self._take(range(max(len(self) - n, 0), len(self)))

    def select(self, *names: str) -> "Table":
        return Table({n: self._cols[n] for n in names})

    def drop(self, *names: str) -> "Table":
        return Table({n: v for n, v in self._cols.items() if n not in names})

    def filter(self, predicate: Callable[[dict[str, Any]], bool]) -> "Table":
        """Keep rows for which ``predicate(row_dict)`` is true."""
        return self._take(i for i, row in enumerate(self.rows()) if predicate(row))

    def sort(self, by: str | list[str], *, descending: bool = False) -> "Table":
        """Sort by one or more columns. ``None`` values always sort last."""
        keys = [by] if isinstance(by, str) else list(by)
        order = list(range(len(self)))
        for key in reversed(keys):  # stable sort, least significant key first
            col = self._cols[key]
            present = [i for i in order if col[i] is not None]
            absent = [i for i in order if col[i] is None]
            present.sort(key=col.__getitem__, reverse=descending)
            order = present + absent
        return self._take(order)

    def with_column(self, name: str, values: Iterable[Any] | Callable[[dict], Any]) -> "Table":
        """Add or replace a column from a list or a ``row -> value`` function."""
        if callable(values):
            values = [values(row) for row in self.rows()]
        cols = dict(self._cols)
        cols[name] = list(values)
        return Table(cols)

    def rename(self, mapping: Mapping[str, str] | Callable[[str], str]) -> "Table":
        fn = mapping if callable(mapping) else (lambda n: mapping.get(n, n))
        new = {}
        for n, v in self._cols.items():
            key = fn(n)
            if key in new:
                raise ValueError(f"rename produces duplicate column {key!r}")
            new[key] = v
        return Table(new)

    # -- cleaning ------------------------------------------------------------

    def normalize_columns(self) -> "Table":
        """Rename columns to snake_case, suffixing duplicates (``a``, ``a_2``)."""
        seen: dict[str, int] = {}
        mapping = {}
        for n in self._cols:
            base = normalize_name(n)
            seen[base] = seen.get(base, 0) + 1
            mapping[n] = base if seen[base] == 1 else f"{base}_{seen[base]}"
        return self.rename(mapping)

    def strip_whitespace(self) -> "Table":
        """Trim strings and collapse internal runs of whitespace."""
        return Table({
            n: [" ".join(x.split()) if isinstance(x, str) else x for x in v]
            for n, v in self._cols.items()
        })

    def standardize_missing(self, missing: Iterable[str] | None = None) -> "Table":
        """Replace NaN and missing tokens ("", "NA", "null", ...) with ``None``."""
        missing = None if missing is None else {m.lower() for m in missing}
        return Table({
            n: [None if is_missing(x, missing) else x for x in v]
            for n, v in self._cols.items()
        })

    def infer_types(self) -> "Table":
        """Convert every column to its inferred type."""
        return Table({n: convert_column(v, infer_type(v)) for n, v in self._cols.items()})

    def astype(self, types: Mapping[str, str]) -> "Table":
        """Convert columns to explicit types; unparseable values become ``None``."""
        cols = dict(self._cols)
        for n, kind in types.items():
            cols[n] = convert_column(cols[n], kind)
        return Table(cols)

    def drop_duplicates(self, subset: Iterable[str] | None = None) -> "Table":
        """Drop repeated rows, keeping the first. Compare on ``subset`` if given."""
        names = list(subset) if subset is not None else self.columns
        seen = set()
        keep = []
        for i in range(len(self)):
            key = tuple(_hashable(self._cols[n][i]) for n in names)
            if key not in seen:
                seen.add(key)
                keep.append(i)
        return self._take(keep)

    def dropna(self, subset: Iterable[str] | None = None, *, how: str = "any") -> "Table":
        """Drop rows with missing values (``how="any"``) or all missing (``"all"``)."""
        if how not in ("any", "all"):
            raise ValueError("how must be 'any' or 'all'")
        names = list(subset) if subset is not None else self.columns
        test = any if how == "any" else all
        return self._take(
            i for i in range(len(self))
            if not test(self._cols[n][i] is None for n in names)
        )

    def drop_empty_columns(self) -> "Table":
        return Table({n: v for n, v in self._cols.items() if any(x is not None for x in v)})

    def fillna(self, value: Any = None, *, strategy: str | None = None,
               columns: Iterable[str] | None = None) -> "Table":
        """Fill ``None`` with a constant, a per-column mapping, or a strategy.

        ``strategy`` is one of ``"mean"``, ``"median"``, ``"mode"``,
        ``"ffill"``, ``"bfill"``. Mean/median only apply to numeric columns.
        """
        names = list(columns) if columns is not None else self.columns
        cols = dict(self._cols)
        for n in names:
            v = cols[n]
            if strategy is None:
                fill = value.get(n) if isinstance(value, Mapping) else value
                if fill is not None:
                    cols[n] = [fill if x is None else x for x in v]
            elif strategy in ("ffill", "bfill"):
                cols[n] = _directional_fill(v, reverse=strategy == "bfill")
            elif strategy in ("mean", "median", "mode"):
                fill = _fill_stat(v, strategy)
                if fill is not None:
                    cols[n] = [fill if x is None else x for x in v]
            else:
                raise ValueError(f"unknown fill strategy {strategy!r}")
        return Table(cols)

    def remove_outliers(self, column: str, *, method: str = "iqr",
                        threshold: float | None = None) -> "Table":
        """Drop rows whose ``column`` value is an outlier.

        ``method="iqr"`` drops values beyond ``threshold`` (default 1.5) IQRs
        outside the quartiles; ``method="zscore"`` drops values more than
        ``threshold`` (default 3) standard deviations from the mean. Rows
        with a missing value are kept.
        """
        mask = analysis.outlier_mask(self._cols[column], method=method, threshold=threshold)
        return self._take(i for i, out in enumerate(mask) if not out)

    def clean(self, *, normalize_names: bool = True, drop_duplicates: bool = True,
              drop_empty: bool = True) -> "Table":
        """Common cleanup pipeline.

        Strips whitespace, standardizes missing values, re-infers types,
        and optionally normalizes column names, drops fully empty
        rows/columns, and drops duplicate rows.
        """
        t = self.strip_whitespace().standardize_missing().infer_types()
        if normalize_names:
            t = t.normalize_columns()
        if drop_empty:
            t = t.dropna(how="all").drop_empty_columns()
        if drop_duplicates:
            t = t.drop_duplicates()
        return t

    # -- analysis ------------------------------------------------------------

    def describe(self, columns: Iterable[str] | None = None) -> "Table":
        """Summary statistics, one row per column. See :func:`analysis.describe`."""
        names = list(columns) if columns is not None else self.columns
        return Table.from_rows(analysis.describe(n, self._cols[n]) for n in names)

    def missing_report(self) -> "Table":
        """Count and percentage of missing values per column."""
        n = len(self)
        return Table.from_rows(
            {"column": c, "missing": m, "percent": round(100 * m / n, 2) if n else 0.0}
            for c, v in self._cols.items()
            for m in [sum(x is None for x in v)]
        )

    def value_counts(self, column: str, *, normalize: bool = False,
                     dropna: bool = True) -> "Table":
        """Frequency of each distinct value, most common first."""
        counts = analysis.value_counts(self._cols[column], dropna=dropna)
        total = sum(counts.values())
        return Table({
            column: list(counts),
            "share" if normalize else "count":
                [c / total for c in counts.values()] if normalize else list(counts.values()),
        })

    def group_by(self, by: str | list[str],
                 aggregations: Mapping[str, str | list[str]]) -> "Table":
        """Group rows and aggregate.

        ``aggregations`` maps a column to one or more of ``count``, ``sum``,
        ``mean``, ``median``, ``min``, ``max``, ``std``, ``nunique``,
        ``first``, ``last``. Output columns are named ``<column>_<agg>``.
        Groups appear in order of first occurrence.
        """
        keys = [by] if isinstance(by, str) else list(by)
        groups: dict[tuple, list[int]] = {}
        for i in range(len(self)):
            groups.setdefault(tuple(self._cols[k][i] for k in keys), []).append(i)
        out_rows = []
        for key, idx in groups.items():
            row = dict(zip(keys, key))
            for col, aggs in aggregations.items():
                for agg in [aggs] if isinstance(aggs, str) else aggs:
                    row[f"{col}_{agg}"] = analysis.aggregate(
                        [self._cols[col][i] for i in idx], agg
                    )
            out_rows.append(row)
        return Table.from_rows(out_rows)

    def corr(self, method: str = "pearson") -> "Table":
        """Pairwise correlation matrix of the numeric columns.

        ``method`` is ``"pearson"`` or ``"spearman"``. Rows with a missing
        value in either column of a pair are ignored for that pair.
        """
        numeric = [n for n, v in self._cols.items() if analysis.is_numeric(v)]
        return Table({"column": numeric} | {
            b: [analysis.correlation(self._cols[a], self._cols[b], method) for a in numeric]
            for b in numeric
        })


def _hashable(x: Any) -> Any:
    try:
        hash(x)
        return x
    except TypeError:
        return repr(x)


def _directional_fill(values: list, *, reverse: bool) -> list:
    seq = reversed(values) if reverse else values
    out, last = [], None
    for x in seq:
        if x is None:
            out.append(last)
        else:
            out.append(x)
            last = x
    return out[::-1] if reverse else out


def _fill_stat(values: list, strategy: str) -> Any:
    if strategy == "mode":
        counts = analysis.value_counts(values)
        return next(iter(counts), None)
    if not analysis.is_numeric(values):
        return None
    return analysis.aggregate(values, strategy)
