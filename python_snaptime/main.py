"""Main package for Python Snaptime."""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import TYPE_CHECKING, overload

import pendulum

from python_snaptime.handlers import handle_timesnapping
from python_snaptime.parsers import parse, to_string

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from python_snaptime.models import Snaptime

__all__ = ["CompiledSnaptime", "apply", "compile", "snap"]


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


@dataclass(frozen=True)
class CompiledSnaptime:
    """A parsed snaptime string that you can apply to many datetimes.

    The class converts a `snaptimes` value of another sequence type to a `tuple`.
    """

    snaptimes: tuple[Snaptime, ...]

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
    def apply(self, dtm: pendulum.DateTime) -> pendulum.DateTime: ...

    @overload
    def apply(self, dtm: dt.datetime) -> dt.datetime: ...

    def apply(self, dtm: pendulum.DateTime | dt.datetime) -> pendulum.DateTime | dt.datetime:
        """Transform a datetime with the snaptimes.

        Args:
            dtm (pendulum.DateTime | dt.datetime): The datetime to be transformed.

        Returns:
            pendulum.DateTime | dt.datetime: The resulting snapped datetime.

        Raises:
            TypeError: If `dtm` is not a `pendulum.DateTime` or a `datetime.datetime`.
        """
        return apply(dtm, self.snaptimes)


def compile(snaptime: str) -> CompiledSnaptime:  # noqa: A001
    """Parse a snaptime string into an object that you can apply to many datetimes.

    Args:
        snaptime (str): The snaptime string to parse, for example `@d-2h`.

    Returns:
        CompiledSnaptime: The parsed snaptime string.

    Raises:
        ValueError: If the snaptime string is invalid.
    """
    return CompiledSnaptime(tuple(parse(snaptime)))
