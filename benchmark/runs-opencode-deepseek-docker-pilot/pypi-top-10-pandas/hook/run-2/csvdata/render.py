"""Plain-text rendering helpers."""

from __future__ import annotations

from .table import Table


def _cell(value):
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def format_table(table, max_rows=None):
    """Render *table* as an aligned, GitHub-flavoured text table."""
    headers = [str(column) for column in table.columns]
    rows = [[_cell(value) for value in row] for row in table.rows]
    truncated = max_rows is not None and len(rows) > max_rows
    if truncated:
        rows = rows[:max_rows]

    widths = [len(header) for header in headers]
    for row in rows:
        for position, value in enumerate(row):
            widths[position] = max(widths[position], len(value))

    def render_row(cells):
        padded = [cell.ljust(widths[i]) for i, cell in enumerate(cells)]
        return "| " + " | ".join(padded) + " |"

    lines = [render_row(headers)]
    lines.append("| " + " | ".join("-" * width for width in widths) + " |")
    lines.extend(render_row(row) for row in rows)
    if truncated:
        lines.append(f"... {len(table) - max_rows} more row(s)")
    return "\n".join(lines)


def format_record(record):
    width = max((len(str(key)) for key in record), default=0)
    return "\n".join(f"{str(key).ljust(width)} : {value}" for key, value in record.items())
