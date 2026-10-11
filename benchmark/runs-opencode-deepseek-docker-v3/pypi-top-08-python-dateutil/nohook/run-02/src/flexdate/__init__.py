"""flexdate: flexible human date parsing and relative date arithmetic."""

from .core import (
    ORDINALS,
    WEEKDAYS,
    first_weekday_of_month,
    last_weekday_of_month,
    nth_weekday_of_month,
    parse_date,
    resolve,
)

__all__ = [
    "ORDINALS",
    "WEEKDAYS",
    "first_weekday_of_month",
    "last_weekday_of_month",
    "nth_weekday_of_month",
    "parse_date",
    "resolve",
]

__version__ = "0.1.0"
