"""Main package for Python Snaptime."""

from __future__ import annotations

import datetime
from typing import overload

import pendulum

from python_snaptime.parsers import parse_snaptime_string

__all__ = ["snap"]


@overload
def snap(dtm: pendulum.DateTime, snap: str) -> pendulum.DateTime: ...


@overload
def snap(dtm: datetime.datetime, snap: str) -> datetime.datetime: ...


def snap(dtm: pendulum.DateTime | datetime.datetime, snap: str) -> pendulum.DateTime | datetime.datetime:
    """Transform datetimes using relative time modifiers.

    Args:
        dtm (pendulum.DateTime | datetime.datetime): The datetime to be transformed.
        snap (str): The snaptime string defining the relative time transformation.

    Returns:
        pendulum.DateTime | datetime.datetime: The resulting snapped datetime.
    """
    if isinstance(dtm, pendulum.DateTime):
        snap_dtm = parse_snaptime_string(snap, dtm)
    elif isinstance(dtm, datetime.datetime):  # pyright: ignore[reportUnnecessaryIsInstance]
        snap_dtm = parse_snaptime_string(snap, pendulum.instance(dtm))
    else:
        raise TypeError("Invalid datetime type. Must be pendulum.DateTime or datetime.datetime.")

    if not isinstance(dtm, pendulum.DateTime):
        if dtm.tzinfo is not None and dtm.tzinfo.utcoffset(dtm) is not None:
            # aware
            snap_dtm = datetime.datetime.fromtimestamp(snap_dtm.timestamp(), tz=snap_dtm.tz)
        else:
            # naive
            snap_dtm = datetime.datetime.fromtimestamp(snap_dtm.timestamp())  # noqa: DTZ006
    return snap_dtm
