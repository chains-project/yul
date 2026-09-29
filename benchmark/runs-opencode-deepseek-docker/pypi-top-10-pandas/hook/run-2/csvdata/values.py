"""Shared helpers for interpreting and classifying cell values."""

MISSING_TOKENS = frozenset(
    {"", "na", "n/a", "nan", "null", "none", "nil", "missing", "?"}
)

TRUE_TOKENS = frozenset({"true", "yes", "y", "t"})
FALSE_TOKENS = frozenset({"false", "no", "n", "f"})

DTYPES = ("int", "float", "bool", "str")


def is_missing(value):
    """Return ``True`` when *value* represents absent data."""
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip().lower() in MISSING_TOKENS
    return False


def looks_like_int(value):
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return True
    if isinstance(value, float):
        return value.is_integer()
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return False
        try:
            int(text)
        except ValueError:
            return False
        return True
    return False


def looks_like_float(value):
    if isinstance(value, bool):
        return False
    if isinstance(value, (int, float)):
        return True
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return False
        try:
            float(text)
        except ValueError:
            return False
        return True
    return False


def looks_like_bool(value):
    if isinstance(value, bool):
        return True
    if isinstance(value, str):
        return value.strip().lower() in TRUE_TOKENS | FALSE_TOKENS
    return False


def parse_bool(value):
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in TRUE_TOKENS:
        return True
    if text in FALSE_TOKENS:
        return False
    raise ValueError(f"cannot interpret {value!r} as a boolean")


def coerce_value(value, dtype):
    """Convert *value* to *dtype*, mapping missing data to ``None``."""
    if is_missing(value):
        return None
    if dtype == "int":
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, float):
            return int(value)
        return int(str(value).strip())
    if dtype == "float":
        if isinstance(value, bool):
            return float(value)
        return float(str(value).strip())
    if dtype == "bool":
        return parse_bool(value)
    return str(value)
