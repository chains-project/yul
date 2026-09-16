"""Relative date arithmetic and natural language date expressions."""

from datetime import datetime
from typing import Optional

from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, WEEKLY, MO, TU, WE, TH, FR, SA, SU

WEEKDAY_MAP = {
    "monday": MO,
    "tuesday": TU,
    "wednesday": WE,
    "thursday": TH,
    "friday": FR,
    "saturday": SA,
    "sunday": SU,
}

MONTH_MAP = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}


class RelativeDate:
    def __init__(self, base: Optional[datetime] = None):
        self.base = base or datetime.now()

    def set_base(self, base: datetime) -> "RelativeDate":
        self.base = base
        return self

    def add(self, **kwargs) -> datetime:
        return self.base + relativedelta(**kwargs)

    def subtract(self, **kwargs) -> datetime:
        return self.base - relativedelta(**kwargs)

    def next(self, unit: Optional[str] = None, weekday: Optional[str] = None) -> datetime:
        if weekday:
            wd = WEEKDAY_MAP[weekday.lower()]
            return self.base + relativedelta(weekday=wd)

        if unit is None:
            return self.base + relativedelta(days=1)

        unit_map = {
            "day": {"days": 1},
            "week": {"weeks": 1},
            "month": {"months": 1},
            "year": {"years": 1},
        }

        if unit not in unit_map:
            raise ValueError(f"Unknown unit: {unit}")

        return self.base + relativedelta(**unit_map[unit])

    def last(self, unit: Optional[str] = None, weekday: Optional[str] = None) -> datetime:
        if weekday:
            wd = WEEKDAY_MAP[weekday.lower()]
            return self.base + relativedelta(weekday=wd, weeks=-1)

        if unit is None:
            return self.base - relativedelta(days=1)

        unit_map = {
            "day": {"days": -1},
            "week": {"weeks": -1},
            "month": {"months": -1},
            "year": {"years": -1},
        }

        if unit not in unit_map:
            raise ValueError(f"Unknown unit: {unit}")

        return self.base + relativedelta(**unit_map[unit])

    def nth_weekday_of_month(
        self,
        n: int,
        weekday_name: str,
        month: Optional[int] = None,
        year: Optional[int] = None,
    ) -> datetime:
        wd = WEEKDAY_MAP[weekday_name.lower()]
        target_year = year or self.base.year
        target_month = month or self.base.month

        first_day = datetime(target_year, target_month, 1)
        weekdays_in_month = list(
            rrule(
                WEEKLY,
                dtstart=first_day,
                byweekday=wd,
                count=5,
                cache=True,
            )
        )

        if n < 1 or n > len(weekdays_in_month):
            raise ValueError(
                f"No {n}th {weekday_name} in {target_month}/{target_year}"
            )

        return weekdays_in_month[n - 1]

    def parse_expression(self, expression: str) -> datetime:
        expr = expression.strip().lower()

        wd_name = None
        for name in WEEKDAY_MAP:
            if name in expr:
                wd_name = name
                break

        month = None
        for name, num in MONTH_MAP.items():
            if name in expr:
                month = num
                break

        if expr == "tomorrow":
            return self.add(days=1)

        if expr == "yesterday":
            return self.subtract(days=1)

        if expr.startswith("in "):
            return self._parse_relative_in(expr)

        if wd_name and "first" in expr:
            year = None
            if "next month" in expr:
                month = self.base.month + 1
                year = self.base.year
                if month > 12:
                    month = 1
                    year += 1
            elif month:
                year = self.base.year
            return self.nth_weekday_of_month(1, wd_name, month, year)

        if wd_name and "second" in expr:
            return self.nth_weekday_of_month(2, wd_name, month or self.base.month, self.base.year)

        if wd_name and "third" in expr:
            return self.nth_weekday_of_month(3, wd_name, month or self.base.month, self.base.year)

        if wd_name and "fourth" in expr:
            return self.nth_weekday_of_month(4, wd_name, month or self.base.month, self.base.year)

        if wd_name and "last" in expr and "month" in expr:
            return self.last(weekday=wd_name)

        if wd_name and "next" in expr:
            return self.next(weekday=wd_name)

        if wd_name and "last" in expr:
            return self.last(weekday=wd_name)

        if "from now" in expr:
            return self._parse_relative(expr, future=True)

        if "ago" in expr:
            return self._parse_relative(expr, future=False)

        if "next month" in expr:
            return self.next("month")

        if "last month" in expr:
            return self.last("month")

        return self.base

    def _parse_relative(self, expr: str, future: bool = True) -> datetime:
        parts = expr.replace("from now", "").replace("ago", "").strip()

        unit_map = {
            "year": "years",
            "month": "months",
            "week": "weeks",
            "day": "days",
            "hour": "hours",
            "minute": "minutes",
            "second": "seconds",
        }

        unit = None
        for word, u in unit_map.items():
            if word in parts:
                parts = parts.replace(word, u)
                unit = u
                break

        if unit is None:
            return self.base

        try:
            amount_str = parts.split()[0]
            amount = int(amount_str)
            if not future:
                amount = -amount
            return self.base + relativedelta(**{unit: amount})
        except (ValueError, IndexError):
            return self.base

    def _parse_relative_in(self, expr: str) -> datetime:
        parts = expr.replace("in ", "", 1).strip()

        unit_map = {
            "year": "years",
            "month": "months",
            "week": "weeks",
            "day": "days",
            "hour": "hours",
            "minute": "minutes",
            "second": "seconds",
        }

        unit = None
        for word, u in unit_map.items():
            if word in parts:
                parts = parts.replace(word, u)
                unit = u
                break

        if unit is None:
            return self.base

        try:
            amount = int(parts.split()[0])
            return self.base + relativedelta(**{unit: amount})
        except (ValueError, IndexError):
            return self.base

    def diff(self, other: datetime, unit: str = "days") -> float:
        delta = other - self.base
        if unit == "years":
            return delta.total_seconds() / (365.25 * 24 * 3600)
        if unit == "months":
            return delta.days / 30.44
        if unit == "weeks":
            return delta.days / 7
        if unit == "days":
            return delta.days
        if unit == "hours":
            return delta.total_seconds() / 3600
        if unit == "minutes":
            return delta.total_seconds() / 60
        if unit == "seconds":
            return delta.total_seconds()
        raise ValueError(f"Unknown unit: {unit}")


def relative_date(expression: str, base: Optional[datetime] = None) -> datetime:
    rd = RelativeDate(base)
    return rd.parse_expression(expression)