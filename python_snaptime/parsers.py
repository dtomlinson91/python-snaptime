"""Module for parsing snaptime strings."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from python_snaptime.handlers import handle_cases
from python_snaptime.models import Snaptime

if TYPE_CHECKING:  # pragma: no cover
    import pendulum


def _parse_raw_snaptime(snaptime: str) -> list[Snaptime]:
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
        raise ValueError("Snaptime string is invalid")
    return results


def parse_snaptime_string(snaptime: str, datetime: pendulum.DateTime) -> pendulum.DateTime:
    """Parse a datetime using a snaptime string.

    Args:
        snaptime (str): The snaptime string defining the relative time transformation.
        datetime (pendulum.DateTime): The datetime to be transformed.

    Returns:
        pendulum.DateTime: The resulting snapped datetime.
    """
    parsed_snaptimes = _parse_raw_snaptime(snaptime)
    for snaptimes in parsed_snaptimes:
        datetime = handle_cases(snaptimes, datetime)
    return datetime
