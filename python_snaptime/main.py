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

__all__ = ["apply", "snap"]


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
