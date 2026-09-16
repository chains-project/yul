"""Parse flexible, human-written date strings."""

from datetime import datetime
from typing import Optional, Tuple

from dateutil import parser as dateutil_parser
from dateutil.parser import ParserError


def parse_date(
    date_string: str,
    default: Optional[datetime] = None,
    ignoretz: bool = False,
    tzinfos: Optional[dict] = None,
) -> datetime:
    if default is None:
        default = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    try:
        result = dateutil_parser.parse(
            date_string,
            default=default,
            ignoretz=ignoretz,
            tzinfos=tzinfos,
        )
        if ":" not in date_string:
            result = result.replace(hour=0, minute=0, second=0, microsecond=0)
        return result
    except ParserError:
        pass

    from .relative import RelativeDate
    rd = RelativeDate(default)
    return rd.parse_expression(date_string)


def parse_date_range(
    start_string: str,
    end_string: str,
) -> Tuple[datetime, datetime]:
    start = parse_date(start_string)
    end = parse_date(end_string)
    return (start, end)


def parse_multiple_dates(date_strings: list[str]) -> list[datetime]:
    return [parse_date(s) for s in date_strings]