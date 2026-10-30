"""Module for parsing snaptime strings."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from python_snaptime.handlers import handle_timesnapping
from python_snaptime.models import Snaptime, Weekday

if TYPE_CHECKING:
    import pendulum


def _parse_raw_snaptime(snaptime: str) -> list[Snaptime]:
    invalid = re.search(r"[^@+\-\w]", snaptime)
    if invalid is not None:
        msg = f"Snaptime string is invalid: unknown character `{invalid.group()}`."
        raise ValueError(msg)

    pattern = r"(([@+-]*)(\d*)(\w*))"
    matches = re.findall(pattern, snaptime)

    results: list[Snaptime] = []
    for match in matches:
        action, integer, unit = match[1] or None, match[2] or None, match[3] or None
        if action is None and integer is None and unit is None:
            pass
        else:
            results.append(
                Snaptime(
                    action=action,
                    unit=unit,
                    time_int=int(integer) if integer is not None else None,
                )
            )

    if not results:
        msg = "Snaptime string is invalid"
        raise ValueError(msg)
    return results


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
    """
    parsed_snaptimes = _parse_raw_snaptime(snaptime)
    for _snaptime in parsed_snaptimes:
        datetime = handle_timesnapping(_snaptime, datetime, week_start=week_start)
    return datetime
