import math


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _numeric_values(table, column):
    return [value for value in table.column(column) if _is_number(value)]


def mean(table, column):
    values = _numeric_values(table, column)
    if not values:
        raise ValueError(f"column {column!r} has no numeric values")
    return sum(values) / len(values)


def median(table, column):
    values = sorted(_numeric_values(table, column))
    size = len(values)
    if size == 0:
        raise ValueError(f"column {column!r} has no numeric values")
    middle = size // 2
    if size % 2:
        return values[middle]
    return (values[middle - 1] + values[middle]) / 2


def mode(table, column):
    values = [value for value in table.column(column) if value is not None]
    if not values:
        raise ValueError(f"column {column!r} has no values")
    counts = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    best = max(counts.values())
    winners = [value for value, count in counts.items() if count == best]
    return winners[0] if len(winners) == 1 else min(winners)


def stdev(table, column, sample=True):
    values = _numeric_values(table, column)
    size = len(values)
    if size < 2:
        raise ValueError(f"column {column!r} needs at least two numeric values")
    average = sum(values) / size
    denominator = size - 1 if sample else size
    return math.sqrt(sum((value - average) ** 2 for value in values) / denominator)


def correlation(table, x_column, y_column):
    pairs = [
        (x, y)
        for x, y in zip(table.column(x_column), table.column(y_column))
        if _is_number(x) and _is_number(y)
    ]
    size = len(pairs)
    if size < 2:
        raise ValueError("need at least two complete numeric pairs")
    mean_x = sum(x for x, _ in pairs) / size
    mean_y = sum(y for _, y in pairs) / size
    covariance = sum((x - mean_x) * (y - mean_y) for x, y in pairs)
    spread_x = math.sqrt(sum((x - mean_x) ** 2 for x, _ in pairs))
    spread_y = math.sqrt(sum((y - mean_y) ** 2 for _, y in pairs))
    if spread_x == 0 or spread_y == 0:
        return 0.0
    return covariance / (spread_x * spread_y)


def value_counts(table, column):
    counts = {}
    for value in table.column(column):
        counts[value] = counts.get(value, 0) + 1
    return counts


def describe(table):
    summary = {}
    for name in table.columns:
        values = table.column(name)
        present = [value for value in values if value is not None]
        entry = {"count": len(present), "missing": len(values) - len(present)}
        numeric = [value for value in values if _is_number(value)]
        if numeric:
            entry["mean"] = sum(numeric) / len(numeric)
            entry["min"] = min(numeric)
            entry["max"] = max(numeric)
        summary[name] = entry
    return summary
