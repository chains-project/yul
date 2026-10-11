"""flexdates: flexible date parsing and relative date arithmetic."""

from .parser import parse_date
from .relative import (
    DateDelta,
    WEEKDAYS,
    add_to_date,
    nth_weekday_of_month,
    weekday_index,
)

__version__ = "0.1.0"

__all__ = [
    "DateDelta",
    "WEEKDAYS",
    "add_to_date",
    "nth_weekday_of_month",
    "parse_date",
    "weekday_index",
]
