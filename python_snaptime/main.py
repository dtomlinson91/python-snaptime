"""Main package for Python Snaptime."""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import TYPE_CHECKING, overload

import pendulum

from python_snaptime.exceptions import SnaptimeError
from python_snaptime.handlers import handle_timesnapping
from python_snaptime.models import Weekday
from python_snaptime.parsers import parse, to_string

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from python_snaptime.models import Snaptime

__all__ = ["CompiledSnaptime", "apply", "compile", "snap", "snap_now", "snap_range"]


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
def apply(dtm: pendulum.DateTime, snaptimes: Sequence[Snaptime], *, week_start: Weekday = ...) -> pendulum.DateTime: ...


@overload
def apply(dtm: dt.datetime, snaptimes: Sequence[Snaptime], *, week_start: Weekday = ...) -> dt.datetime: ...


def apply(
    dtm: pendulum.DateTime | dt.datetime, snaptimes: Sequence[Snaptime], *, week_start: Weekday = Weekday.MONDAY
) -> pendulum.DateTime | dt.datetime:
    """Transform a datetime with snaptimes from `parse`.

    Args:
        dtm (pendulum.DateTime | dt.datetime): The datetime to be transformed.
        snaptimes (Sequence[Snaptime]): The snaptimes to apply, in order.
        week_start (Weekday): The first day of the week for `@w`. The default is Monday.

    Returns:
        pendulum.DateTime | dt.datetime: The resulting snapped datetime.

    Raises:
        TypeError: If `dtm` is not a `pendulum.DateTime` or a `datetime.datetime`.
    """

    def _apply_snaptimes(pendulum_dtm: pendulum.DateTime) -> pendulum.DateTime:
        for snaptime in snaptimes:
            pendulum_dtm = handle_timesnapping(snaptime, pendulum_dtm, week_start=week_start)
        return pendulum_dtm

    return _transform_datetime(dtm, _apply_snaptimes)


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

    Raises:
        SnaptimeError: If the snaptime string is invalid.
        TypeError: If `dtm` is not a `pendulum.DateTime` or a `datetime.datetime`.
    """
    return apply(dtm, parse(snap), week_start=week_start)


@overload
def snap_range(
    dtm: pendulum.DateTime, start: str, end: str, *, inclusive: bool = False, week_start: Weekday = ...
) -> tuple[pendulum.DateTime, pendulum.DateTime]: ...


@overload
def snap_range(
    dtm: dt.datetime, start: str, end: str, *, inclusive: bool = False, week_start: Weekday = ...
) -> tuple[dt.datetime, dt.datetime]: ...


def snap_range(
    dtm: pendulum.DateTime | dt.datetime,
    start: str,
    end: str,
    *,
    inclusive: bool = False,
    week_start: Weekday = Weekday.MONDAY,
) -> tuple[pendulum.DateTime, pendulum.DateTime] | tuple[dt.datetime, dt.datetime]:
    """Get the start and the end of a range from two snaptime strings.

    Args:
        dtm (pendulum.DateTime | dt.datetime): The datetime to be transformed.
        start (str): The snaptime string for the start of the range.
        end (str): The snaptime string for the end of the range.
        inclusive (bool): If True, the end is the last microsecond in the range. If False, the end is
            the first microsecond after the range.
        week_start (Weekday): The first day of the week for `@w`. The default is Monday.

    Returns:
        tuple[pendulum.DateTime, pendulum.DateTime] | tuple[dt.datetime, dt.datetime]: The start and
            the end of the range.

    Raises:
        SnaptimeError: If a snaptime string is invalid, if the start is after the end, or if `inclusive`
            is True and the range is empty.
    """
    start_dtm = snap(dtm, start, week_start=week_start)
    end_dtm = snap(dtm, end, week_start=week_start)
    if start_dtm > end_dtm:
        msg = f"The start of the range ({start!r}) is after the end ({end!r})."
        raise SnaptimeError(msg)
    if inclusive:
        if start_dtm == end_dtm:
            msg = f"The range from {start!r} to {end!r} is empty. An inclusive range must not be empty."
            raise SnaptimeError(msg)
        end_dtm -= dt.timedelta(microseconds=1)
    return start_dtm, end_dtm


@overload
def snap_now(
    snaptime: str,
    tz: str | pendulum.Timezone | pendulum.FixedTimezone | None = None,
    *,
    week_start: Weekday = ...,
) -> pendulum.DateTime: ...


@overload
def snap_now(snaptime: str, tz: dt.tzinfo, *, week_start: Weekday = ...) -> dt.datetime: ...


def snap_now(
    snaptime: str, tz: str | dt.tzinfo | None = None, *, week_start: Weekday = Weekday.MONDAY
) -> pendulum.DateTime | dt.datetime:
    """Transform the current time using relative time modifiers.

    Args:
        snaptime (str): The snaptime string defining the relative time transformation.
        tz (str | dt.tzinfo | None): The timezone of the current time. Defaults to UTC. A timezone name, a
            pendulum timezone or None gives a pendulum.DateTime. Any other tzinfo, for example a
            zoneinfo.ZoneInfo, gives a datetime.datetime.
        week_start (Weekday): The first day of the week for `@w`. The default is Monday.

    Returns:
        pendulum.DateTime | dt.datetime: The resulting snapped datetime in the timezone `tz`.
    """
    now = pendulum.now("UTC")
    if tz is None:
        return snap(now, snaptime, week_start=week_start)
    if isinstance(tz, (str, pendulum.Timezone, pendulum.FixedTimezone)):
        return snap(now.in_timezone(tz), snaptime, week_start=week_start)
    return snap(dt.datetime.combine(now.date(), now.time(), now.tzinfo).astimezone(tz), snaptime, week_start=week_start)


@dataclass(frozen=True)
class CompiledSnaptime:
    """A parsed snaptime string that you can apply to many datetimes.

    The class converts a `snaptimes` value of another sequence type to a `tuple`.
    """

    snaptimes: tuple[Snaptime, ...]
    week_start: Weekday = Weekday.MONDAY

    def __post_init__(self) -> None:
        """Convert the snaptimes to a tuple."""
        # frozen dataclasses block normal attribute assignment
        object.__setattr__(self, "snaptimes", tuple(self.snaptimes))

    def __str__(self) -> str:
        """Return the snaptime string of the snaptimes, for example `@d-2h`.

        Returns:
            str: The snaptime string.
        """
        return to_string(self.snaptimes)

    @overload
    def apply(self, dtm: pendulum.DateTime, *, week_start: Weekday | None = ...) -> pendulum.DateTime: ...

    @overload
    def apply(self, dtm: dt.datetime, *, week_start: Weekday | None = ...) -> dt.datetime: ...

    def apply(
        self, dtm: pendulum.DateTime | dt.datetime, *, week_start: Weekday | None = None
    ) -> pendulum.DateTime | dt.datetime:
        """Transform a datetime with the snaptimes.

        Args:
            dtm (pendulum.DateTime | dt.datetime): The datetime to be transformed.
            week_start (Weekday | None): The first day of the week for `@w`. The default is the
                `week_start` of this object.

        Returns:
            pendulum.DateTime | dt.datetime: The resulting snapped datetime.

        Raises:
            TypeError: If `dtm` is not a `pendulum.DateTime` or a `datetime.datetime`.
        """
        return apply(dtm, self.snaptimes, week_start=self.week_start if week_start is None else week_start)


def compile(snaptime: str, *, week_start: Weekday = Weekday.MONDAY) -> CompiledSnaptime:  # noqa: A001
    """Parse a snaptime string into an object that you can apply to many datetimes.

    Args:
        snaptime (str): The snaptime string to parse, for example `@d-2h`.
        week_start (Weekday): The first day of the week for `@w`. The default is Monday.

    Returns:
        CompiledSnaptime: The parsed snaptime string.

    Raises:
        SnaptimeError: If the snaptime string is invalid.
    """
    return CompiledSnaptime(tuple(parse(snaptime)), week_start=week_start)
