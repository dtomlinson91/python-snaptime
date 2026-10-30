"""Main package for Python Snaptime."""

from __future__ import annotations

import datetime as dt
from typing import overload

import pendulum

from python_snaptime.parsers import parse_snaptime_string

__all__ = ["snap", "snap_range"]


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


@overload
def snap_range(
    dtm: pendulum.DateTime, start: str, end: str, *, inclusive: bool = False
) -> tuple[pendulum.DateTime, pendulum.DateTime]: ...


@overload
def snap_range(
    dtm: dt.datetime, start: str, end: str, *, inclusive: bool = False
) -> tuple[dt.datetime, dt.datetime]: ...


def snap_range(
    dtm: pendulum.DateTime | dt.datetime, start: str, end: str, *, inclusive: bool = False
) -> tuple[pendulum.DateTime, pendulum.DateTime] | tuple[dt.datetime, dt.datetime]:
    """Get the start and the end of a range from two snaptime strings.

    Args:
        dtm (pendulum.DateTime | dt.datetime): The datetime to be transformed.
        start (str): The snaptime string for the start of the range.
        end (str): The snaptime string for the end of the range.
        inclusive (bool): If True, the end is the last microsecond in the range. If False, the end is
            the first microsecond after the range.

    Returns:
        tuple[pendulum.DateTime, pendulum.DateTime] | tuple[dt.datetime, dt.datetime]: The start and
            the end of the range.

    Raises:
        ValueError: If the start is after the end, or if `inclusive` is True and the range is empty.
    """
    start_dtm = snap(dtm, start)
    end_dtm = snap(dtm, end)
    if start_dtm > end_dtm:
        msg = f"The start of the range ({start!r}) is after the end ({end!r})."
        raise ValueError(msg)
    if inclusive:
        if start_dtm == end_dtm:
            msg = f"The range from {start!r} to {end!r} is empty. An inclusive range must not be empty."
            raise ValueError(msg)
        end_dtm -= dt.timedelta(microseconds=1)
    return start_dtm, end_dtm
