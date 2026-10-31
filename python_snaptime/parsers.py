"""Module for parsing snaptime strings."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Final

from python_snaptime.exceptions import SnaptimeError
from python_snaptime.handlers import handle_timesnapping
from python_snaptime.models import Snaptime, Unit, Weekday

if TYPE_CHECKING:
    from collections.abc import Iterable

    import pendulum

NOW: Final = "now"
"""The snaptime string for the current time, which leaves a datetime unchanged."""

_SPLUNK_WEEKDAYS = frozenset("01234567")


def _parse_weekday(unit: str | None) -> Weekday | None:
    weekday_match = re.fullmatch(r"w(\d+)", unit or "")
    if weekday_match is None:
        return None
    number = weekday_match.group(1)
    if number not in _SPLUNK_WEEKDAYS:
        msg = f"Snaptime string is invalid: the day of the week must be `w0` to `w7`, but `{unit}` is not."
        raise SnaptimeError(msg)
    # Splunk numbers Sunday as 0 or 7 and Monday as 1
    return Weekday((int(number) - 1) % 7)


def parse(snaptime: str) -> list[Snaptime]:
    """Parse a snaptime string into a list of snaptimes.

    Args:
        snaptime (str): The snaptime string to parse, for example `@d-2h+10m`.

    Returns:
        list[Snaptime]: The snaptimes in the order that they occur in the string. The snaptime string
            `now` gives an empty list.

    Raises:
        SnaptimeError: If the snaptime string is invalid.
    """
    if snaptime == NOW:
        return []
    if NOW in snaptime.lower():
        msg = f"Snaptime string is invalid: `{NOW}` must be the whole snaptime string, in lower case."
        raise SnaptimeError(msg)

    invalid = re.search(r"[^@+\-\w]", snaptime)
    if invalid is not None:
        msg = f"Snaptime string is invalid: unknown character `{invalid.group()}`."
        raise SnaptimeError(msg)

    pattern = r"(([@+-]*)(\d*)(\w*))"
    matches = re.findall(pattern, snaptime)

    results: list[Snaptime] = []
    for match in matches:
        action, integer, unit = match[1] or None, match[2] or None, match[3] or None
        if action is None and integer is None and unit is None:
            pass
        else:
            weekday = _parse_weekday(unit)
            results.append(
                Snaptime(
                    action=action,
                    unit=unit if weekday is None else Unit.WEEK,
                    time_int=int(integer) if integer is not None else None,
                    weekday=weekday,
                )
            )

    if not results:
        msg = "Snaptime string is invalid"
        raise SnaptimeError(msg)
    return results


def is_valid(snaptime: str) -> bool:
    """Check if a snaptime string is valid.

    Args:
        snaptime (str): The snaptime string to check, for example `@d-2h`.

    Returns:
        bool: `True` if `parse` accepts the snaptime string, else `False`.
    """
    try:
        parse(snaptime)
    except SnaptimeError:
        return False
    return True


def to_string(snaptimes: Iterable[Snaptime]) -> str:
    """Convert snaptimes to a snaptime string.

    Args:
        snaptimes (Iterable[Snaptime]): The snaptimes to convert, in the order to apply them.

    Returns:
        str: The snaptime string, for example `@d-2h`. No snaptimes give `now`.
    """
    return "".join(str(snaptime) for snaptime in snaptimes) or NOW


def parse_snaptime_string(
    snaptime: str, datetime: pendulum.DateTime, *, week_start: Weekday = Weekday.MONDAY
) -> pendulum.DateTime:
    """Parse a datetime using a snaptime string.

    Args:
        snaptime (str): The snaptime string defining the relative time transformation.
        datetime (pendulum.DateTime): The datetime to be transformed.
        week_start (Weekday): The first day of the week for `@w`. The default is Monday.

    Returns:
        pendulum.DateTime: The resulting snapped datetime.

    Raises:
        SnaptimeError: If the snaptime string is invalid.
    """
    parsed_snaptimes = parse(snaptime)
    for _snaptime in parsed_snaptimes:
        datetime = handle_timesnapping(_snaptime, datetime, week_start=week_start)
    return datetime
