"""Relative date arithmetic helpers built on :mod:`dateutil.relativedelta`."""

from __future__ import annotations

from datetime import date, datetime
from typing import TypeVar

from dateutil.relativedelta import relativedelta

_D = TypeVar("_D", date, datetime)


def shift(value: _D, **units: int) -> _D:
    """Shift ``value`` by any ``relativedelta`` units.

    >>> from datetime import date
    >>> shift(date(2026, 10, 31), months=1)
    datetime.date(2026, 11, 30)
    """
    return value + relativedelta(**units)
