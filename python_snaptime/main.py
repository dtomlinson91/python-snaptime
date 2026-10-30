"""Main package for Python Snaptime."""

from __future__ import annotations

import datetime as dt
from typing import TYPE_CHECKING, overload

import pendulum

from python_snaptime.handlers import handle_timesnapping
from python_snaptime.parsers import parse

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from python_snaptime.models import Snaptime

__all__ = ["apply", "snap", "snap_now", "snap_range"]


def _transform_datetime(
    dtm: pendulum.DateTime | dt.datetime,
    transform: Callable[[pendulum.DateTime], pendulum.DateTime],
) -> pendulum.DateTime | dt.datetime:
    if isinstance(dtm, pendulum.DateTime):
        return transform(dtm)
    if not isinstance(dtm, dt.datetime):  # pyright: ignore[reportUnnecessaryIsInstance]
        msg = "Invalid datetime type. Must be pendulum.DateTime or datetime.datetime."
        raise TypeError(msg)

    result = transform(pendulum.instance(dtm))
    if dtm.tzinfo is not None and dtm.tzinfo.utcoffset(dtm) is not None:
        # aware
        return dt.datetime.fromtimestamp(result.timestamp(), tz=dtm.tzinfo)
    # naive
    return dt.datetime.combine(result.date(), result.time())


@overload
def apply(dtm: pendulum.DateTime, snaptimes: Sequence[Snaptime]) -> pendulum.DateTime: ...


@overload
def apply(dtm: dt.datetime, snaptimes: Sequence[Snaptime]) -> dt.datetime: ...


def apply(dtm: pendulum.DateTime | dt.datetime, snaptimes: Sequence[Snaptime]) -> pendulum.DateTime | dt.datetime:
    """Transform a datetime with snaptimes from `parse`.

    Args:
        dtm (pendulum.DateTime | dt.datetime): The datetime to be transformed.
        snaptimes (Sequence[Snaptime]): The snaptimes to apply, in order.

    Returns:
        pendulum.DateTime | dt.datetime: The resulting snapped datetime.

    Raises:
        TypeError: If `dtm` is not a `pendulum.DateTime` or a `datetime.datetime`.
    """

    def _apply_snaptimes(pendulum_dtm: pendulum.DateTime) -> pendulum.DateTime:
        for snaptime in snaptimes:
            pendulum_dtm = handle_timesnapping(snaptime, pendulum_dtm)
        return pendulum_dtm

    return _transform_datetime(dtm, _apply_snaptimes)


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
    return apply(dtm, parse(snap))


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


@overload
def snap_now(
    snaptime: str, tz: str | pendulum.Timezone | pendulum.FixedTimezone | None = None
) -> pendulum.DateTime: ...


@overload
def snap_now(snaptime: str, tz: dt.tzinfo) -> dt.datetime: ...


def snap_now(snaptime: str, tz: str | dt.tzinfo | None = None) -> pendulum.DateTime | dt.datetime:
    """Transform the current time using relative time modifiers.

    Args:
        snaptime (str): The snaptime string defining the relative time transformation.
        tz (str | dt.tzinfo | None): The timezone of the current time. Defaults to UTC. A timezone name, a
            pendulum timezone or None gives a pendulum.DateTime. Any other tzinfo, for example a
            zoneinfo.ZoneInfo, gives a datetime.datetime.

    Returns:
        pendulum.DateTime | dt.datetime: The resulting snapped datetime in the timezone `tz`.
    """
    now = pendulum.now("UTC")
    if tz is None:
        return snap(now, snaptime)
    if isinstance(tz, (str, pendulum.Timezone, pendulum.FixedTimezone)):
        return snap(now.in_timezone(tz), snaptime)
    return snap(dt.datetime.combine(now.date(), now.time(), now.tzinfo).astimezone(tz), snaptime)
