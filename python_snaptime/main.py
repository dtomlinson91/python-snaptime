"""Main package for Python Snaptime."""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import TYPE_CHECKING, overload

import pendulum

from python_snaptime.exceptions import SnaptimeError
from python_snaptime.handlers import handle_timesnapping
from python_snaptime.models import Unit, Weekday
from python_snaptime.parsers import parse, to_string

if TYPE_CHECKING:
    from collections.abc import Sequence

    from python_snaptime.models import Snaptime

__all__ = ["CompiledSnaptime", "apply", "compile", "snap", "snap_now", "snap_range"]


_DATE_UNITS = frozenset({Unit.DAY, Unit.WEEK, Unit.MONTH, Unit.QUARTER, Unit.YEAR})


def _apply_snaptimes(dtm: pendulum.DateTime, snaptimes: Sequence[Snaptime], week_start: Weekday) -> pendulum.DateTime:
    for snaptime in snaptimes:
        dtm = handle_timesnapping(snaptime, dtm, week_start=week_start)
    return dtm


def _apply_snaptimes_to_date(date: dt.date, snaptimes: Sequence[Snaptime], week_start: Weekday) -> pendulum.DateTime:
    for snaptime in snaptimes:
        if snaptime.unit not in _DATE_UNITS:
            unit = snaptime.unit.value[0] if snaptime.unit is not None else None
            msg = f"Cannot apply {str(snaptime)!r} to a date: the unit {unit!r} is smaller than a day."
            raise SnaptimeError(msg)
    midnight = pendulum.datetime(date.year, date.month, date.day, tz=None)
    return _apply_snaptimes(midnight, snaptimes, week_start)


def _transform_datetime(
    dtm: pendulum.DateTime | dt.datetime | pendulum.Date | dt.date,
    snaptimes: Sequence[Snaptime],
    week_start: Weekday,
) -> pendulum.DateTime | dt.datetime | pendulum.Date | dt.date:
    if isinstance(dtm, pendulum.DateTime):
        return _apply_snaptimes(dtm, snaptimes, week_start)
    if isinstance(dtm, dt.datetime):
        result = _apply_snaptimes(pendulum.instance(dtm), snaptimes, week_start)
        if dtm.tzinfo is not None and dtm.tzinfo.utcoffset(dtm) is not None:
            # aware
            return dt.datetime.fromtimestamp(result.timestamp(), tz=dtm.tzinfo)
        # naive
        return dt.datetime.combine(result.date(), result.time())
    if isinstance(dtm, pendulum.Date):
        return _apply_snaptimes_to_date(dtm, snaptimes, week_start).date()
    if not isinstance(dtm, dt.date):  # pyright: ignore[reportUnnecessaryIsInstance]
        msg = "Invalid datetime type. Must be pendulum.DateTime, datetime.datetime, pendulum.Date or datetime.date."
        raise TypeError(msg)
    result = _apply_snaptimes_to_date(dtm, snaptimes, week_start)
    return dt.date(result.year, result.month, result.day)


@overload
def apply(dtm: pendulum.DateTime, snaptimes: Sequence[Snaptime], *, week_start: Weekday = ...) -> pendulum.DateTime: ...


@overload
def apply(dtm: dt.datetime, snaptimes: Sequence[Snaptime], *, week_start: Weekday = ...) -> dt.datetime: ...


@overload
def apply(dtm: pendulum.Date, snaptimes: Sequence[Snaptime], *, week_start: Weekday = ...) -> pendulum.Date: ...


@overload
def apply(dtm: dt.date, snaptimes: Sequence[Snaptime], *, week_start: Weekday = ...) -> dt.date: ...


def apply(
    dtm: pendulum.DateTime | dt.datetime | pendulum.Date | dt.date,
    snaptimes: Sequence[Snaptime],
    *,
    week_start: Weekday = Weekday.MONDAY,
) -> pendulum.DateTime | dt.datetime | pendulum.Date | dt.date:
    """Transform a datetime or a date with snaptimes from `parse`.

    A date takes only snaptimes with a unit of a day or larger. The function returns the type of `dtm`.

    Args:
        dtm (pendulum.DateTime | dt.datetime | pendulum.Date | dt.date): The datetime or the date to be transformed.
        snaptimes (Sequence[Snaptime]): The snaptimes to apply, in order.
        week_start (Weekday): The first day of the week for `@w`. The default is Monday.

    Returns:
        pendulum.DateTime | dt.datetime | pendulum.Date | dt.date: The resulting snapped datetime or date.

    Raises:
        SnaptimeError: If `dtm` is a date and a snaptime has a unit smaller than a day.
        TypeError: If `dtm` is not a `pendulum.DateTime`, a `datetime.datetime`, a `pendulum.Date` or a
            `datetime.date`.
    """
    return _transform_datetime(dtm, snaptimes, week_start)


@overload
def snap(dtm: pendulum.DateTime, snap: str, *, week_start: Weekday = ...) -> pendulum.DateTime: ...


@overload
def snap(dtm: dt.datetime, snap: str, *, week_start: Weekday = ...) -> dt.datetime: ...


@overload
def snap(dtm: pendulum.Date, snap: str, *, week_start: Weekday = ...) -> pendulum.Date: ...


@overload
def snap(dtm: dt.date, snap: str, *, week_start: Weekday = ...) -> dt.date: ...


def snap(
    dtm: pendulum.DateTime | dt.datetime | pendulum.Date | dt.date, snap: str, *, week_start: Weekday = Weekday.MONDAY
) -> pendulum.DateTime | dt.datetime | pendulum.Date | dt.date:
    """Transform datetimes or dates using relative time modifiers.

    A date takes only units of a day or larger. The function returns the type of `dtm`.

    Args:
        dtm (pendulum.DateTime | dt.datetime | pendulum.Date | dt.date): The datetime or the date to be transformed.
        snap (str): The snaptime string defining the relative time transformation.
        week_start (Weekday): The first day of the week for `@w`. The default is Monday.

    Returns:
        pendulum.DateTime | dt.datetime | pendulum.Date | dt.date: The resulting snapped datetime or date.

    Raises:
        SnaptimeError: If the snaptime string is invalid, or if `dtm` is a date and the snaptime string
            has a unit smaller than a day.
        TypeError: If `dtm` is not a `pendulum.DateTime`, a `datetime.datetime`, a `pendulum.Date` or a
            `datetime.date`.
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


@overload
def snap_range(
    dtm: pendulum.Date, start: str, end: str, *, inclusive: bool = False, week_start: Weekday = ...
) -> tuple[pendulum.Date, pendulum.Date]: ...


@overload
def snap_range(
    dtm: dt.date, start: str, end: str, *, inclusive: bool = False, week_start: Weekday = ...
) -> tuple[dt.date, dt.date]: ...


def snap_range(
    dtm: pendulum.DateTime | dt.datetime | pendulum.Date | dt.date,
    start: str,
    end: str,
    *,
    inclusive: bool = False,
    week_start: Weekday = Weekday.MONDAY,
) -> (
    tuple[pendulum.DateTime, pendulum.DateTime]
    | tuple[dt.datetime, dt.datetime]
    | tuple[pendulum.Date, pendulum.Date]
    | tuple[dt.date, dt.date]
):
    """Get the start and the end of a range from two snaptime strings.

    Args:
        dtm (pendulum.DateTime | dt.datetime | pendulum.Date | dt.date): The datetime or the date to be transformed.
        start (str): The snaptime string for the start of the range.
        end (str): The snaptime string for the end of the range.
        inclusive (bool): If True, the end is the last microsecond in the range, or the last day for a
            date. If False, the end is the first microsecond or the first day after the range.
        week_start (Weekday): The first day of the week for `@w`. The default is Monday.

    Returns:
        tuple[pendulum.DateTime, pendulum.DateTime] | tuple[dt.datetime, dt.datetime] |
            tuple[pendulum.Date, pendulum.Date] | tuple[dt.date, dt.date]: The start and the end of the
            range, with the type of `dtm`.

    Raises:
        SnaptimeError: If a snaptime string is invalid, if the start is after the end, if `inclusive`
            is True and the range is empty, or if `dtm` is a date and a snaptime string has a unit
            smaller than a day.
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
        end_dtm -= dt.timedelta(microseconds=1) if isinstance(end_dtm, dt.datetime) else dt.timedelta(days=1)
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

    @overload
    def apply(self, dtm: pendulum.Date, *, week_start: Weekday | None = ...) -> pendulum.Date: ...

    @overload
    def apply(self, dtm: dt.date, *, week_start: Weekday | None = ...) -> dt.date: ...

    def apply(
        self, dtm: pendulum.DateTime | dt.datetime | pendulum.Date | dt.date, *, week_start: Weekday | None = None
    ) -> pendulum.DateTime | dt.datetime | pendulum.Date | dt.date:
        """Transform a datetime or a date with the snaptimes.

        A date takes only snaptimes with a unit of a day or larger. The method returns the type of `dtm`.

        Args:
            dtm (pendulum.DateTime | dt.datetime | pendulum.Date | dt.date): The datetime or the date to be transformed.
            week_start (Weekday | None): The first day of the week for `@w`. The default is the
                `week_start` of this object.

        Returns:
            pendulum.DateTime | dt.datetime | pendulum.Date | dt.date: The resulting snapped datetime or date.

        Raises:
            SnaptimeError: If `dtm` is a date and a snaptime has a unit smaller than a day.
            TypeError: If `dtm` is not a `pendulum.DateTime`, a `datetime.datetime`, a `pendulum.Date` or
                a `datetime.date`.
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
