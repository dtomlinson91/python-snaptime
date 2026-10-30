"""Main package for Python Snaptime."""

from __future__ import annotations

import datetime as dt
from typing import overload

import pendulum

from python_snaptime.parsers import parse_snaptime_string

__all__ = ["snap"]


@overload
def snap(dtm: pendulum.DateTime, snap: str) -> pendulum.DateTime: ...


@overload
def snap(dtm: dt.datetime, snap: str) -> dt.datetime: ...


def snap(dtm: pendulum.DateTime | dt.datetime, snap: str) -> pendulum.DateTime | dt.datetime:
    """Transform datetimes using relative time modifiers.

    Args:
        dtm (pendulum.DateTime | dt.datetime): The datetime to be transformed.
        snap (str): The snaptime string defining the relative time transformation.

    Returns:
        pendulum.DateTime | dt.datetime: The resulting snapped datetime.

    Raises:
        SnaptimeError: If the snaptime string is invalid.
        TypeError: If `dtm` is not a `pendulum.DateTime` or a `datetime.datetime`.
    """
    if isinstance(dtm, pendulum.DateTime):
        snap_dtm = parse_snaptime_string(snap, dtm)
    elif isinstance(dtm, dt.datetime):  # pyright: ignore[reportUnnecessaryIsInstance]
        snap_dtm = parse_snaptime_string(snap, pendulum.instance(dtm))
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
