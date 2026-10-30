"""Main package for Python Snaptime."""

from __future__ import annotations

import datetime as dt
from typing import overload

import pendulum

from python_snaptime.models import Weekday
from python_snaptime.parsers import parse_snaptime_string

__all__ = ["snap"]


@overload
def snap(dtm: pendulum.DateTime, snap: str, *, week_start: Weekday = ...) -> pendulum.DateTime: ...


@overload
def snap(dtm: dt.datetime, snap: str, *, week_start: Weekday = ...) -> dt.datetime: ...


def snap(
    dtm: pendulum.DateTime | dt.datetime, snap: str, *, week_start: Weekday = Weekday.MONDAY
) -> pendulum.DateTime | dt.datetime:
    """Transform datetimes using relative time modifiers.

    Args:
        dtm (pendulum.DateTime | dt.datetime): The datetime to be transformed.
        snap (str): The snaptime string defining the relative time transformation.
        week_start (Weekday): The first day of the week for `@w`. The default is Monday.

    Returns:
        pendulum.DateTime | dt.datetime: The resulting snapped datetime.
    """
    if isinstance(dtm, pendulum.DateTime):
        snap_dtm = parse_snaptime_string(snap, dtm, week_start=week_start)
    elif isinstance(dtm, dt.datetime):  # pyright: ignore[reportUnnecessaryIsInstance]
        snap_dtm = parse_snaptime_string(snap, pendulum.instance(dtm), week_start=week_start)
    else:
        msg = "Invalid datetime type. Must be pendulum.DateTime or datetime.datetime."
        raise TypeError(msg)

    if not isinstance(dtm, pendulum.DateTime):
        if dtm.tzinfo is not None and dtm.tzinfo.utcoffset(dtm) is not None:
            # aware
            snap_dtm = dt.datetime.fromtimestamp(snap_dtm.timestamp(), tz=dtm.tzinfo)
        else:
            # naive
            snap_dtm = dt.datetime.combine(snap_dtm.date(), snap_dtm.time())
    return snap_dtm
