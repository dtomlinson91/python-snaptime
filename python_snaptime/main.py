"""Main package for Python Snaptime."""

from __future__ import annotations

import datetime as dt
from typing import overload

import pendulum

from python_snaptime.parsers import parse_snaptime_string

__all__ = ["snap", "snap_now"]


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


def snap_now(snaptime: str, tz: str | dt.tzinfo | None = None) -> pendulum.DateTime:
    """Transform the current time using relative time modifiers.

    Args:
        snaptime (str): The snaptime string defining the relative time transformation.
        tz (str | dt.tzinfo | None): The timezone of the current time. Defaults to UTC.

    Returns:
        pendulum.DateTime: The resulting snapped datetime in the timezone `tz`.
    """
    now = pendulum.now(tz if isinstance(tz, str) else "UTC")
    if isinstance(tz, dt.tzinfo):
        # pendulum loses a non-pendulum tzinfo when it snaps, so convert it to a pendulum timezone
        now = pendulum.instance(dt.datetime.combine(now.date(), now.time(), now.tzinfo).astimezone(tz))
    return snap(now, snaptime)
