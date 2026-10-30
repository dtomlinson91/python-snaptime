"""Module defining models for python-snaptime."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from python_snaptime.exceptions import SnaptimeError


class Action(str, Enum):
    """Time Snapping Actions."""

    SNAP = "@"
    ADD = "+"
    SUB = "-"


class Unit(Enum):
    """Time Units."""

    MICROSECOND = "us", "microsecond", "microseconds"
    MILLISECOND = "ms", "millisecond", "milliseconds"
    SECOND = "s", "sec", "secs", "second", "seconds"
    MINUTE = "m", "min", "mins", "minute", "minutes"
    HOUR = "h", "hr", "hrs", "hour", "hours"
    DAY = "d", "day", "days"
    WEEK = "w", "week", "weeks"
    MONTH = "mon", "month", "months"
    QUARTER = "q", "qtr", "qtrs", "quarter", "quarters"
    YEAR = "y", "yr", "yrs", "year", "years"

    @classmethod
    def _missing_(cls, value: object):  # noqa: ANN206
        for member in cls:
            if value in member.value:
                return member
        return None  # pragma: no cover


class Weekday(int, Enum):
    """Days of the week, numbered like `datetime.weekday()`."""

    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


_SNAP_MULTIPLE_LIMITS = {Unit.SECOND: 60, Unit.MINUTE: 60, Unit.HOUR: 24}


def _verify_snap_multiple(unit: Unit, time_int: int) -> None:
    limit = _SNAP_MULTIPLE_LIMITS.get(unit)
    if limit is None:
        msg = "Snaptime string is invalid: can only snap to a multiple of seconds, minutes or hours."
        raise SnaptimeError(msg)
    if time_int < 1 or limit % time_int != 0:
        msg = f"Snaptime string is invalid: a snap multiple must divide {limit}, but {time_int} does not."
        raise SnaptimeError(msg)


@dataclass(frozen=True, kw_only=True)
class Snaptime:
    """Model representing a snaptime configuration.

    The class converts a `str` value of `action` or `unit` to its `Action` or `Unit` member.

    Raises:
        SnaptimeError: If the configuration is not a valid snaptime operation.
    """

    action: Action | None = None
    unit: Unit | None = None
    time_int: int | None = None

    def __str__(self) -> str:
        """Return the snaptime string of this snaptime, for example `@d`, `@15m` or `-2h`.

        Returns:
            str: The snaptime string, with the shortest string of the unit.
        """
        action = self.action.value if self.action is not None else ""
        time_int = str(self.time_int) if self.time_int is not None else ""
        unit = self.unit.value[0] if self.unit is not None else ""
        return f"{action}{time_int}{unit}"

    def __post_init__(self) -> None:
        """Convert the action and the unit to enums, then validate the configuration."""
        if self.action is None:
            msg = "Snaptime string is invalid: must provide either a snap `@` or time delta `+-`."
            raise SnaptimeError(msg)
        try:
            # frozen dataclasses block normal attribute assignment
            object.__setattr__(self, "action", Action(self.action))
            if self.unit is not None:
                object.__setattr__(self, "unit", Unit(self.unit))
        except ValueError as exc:
            raise SnaptimeError(str(exc)) from exc

        if self.action == Action.SNAP:
            if self.unit is None:
                msg = "Snaptime string is invalid: missing time unit when snapping."
                raise SnaptimeError(msg)
            if self.unit == Unit.MILLISECOND:
                msg = "Snaptime string is invalid: cannot snap to nearest millisecond."
                raise SnaptimeError(msg)
            if self.unit == Unit.MICROSECOND:
                msg = "Snaptime string is invalid: cannot snap to nearest microsecond."
                raise SnaptimeError(msg)
            if self.time_int is not None:
                _verify_snap_multiple(self.unit, self.time_int)
        else:
            if self.time_int is None:
                msg = "Snaptime string is invalid: missing time integer for time addition or subtraction."
                raise SnaptimeError(msg)
            if self.time_int < 0:
                msg = "Snaptime string is invalid: time integer cannot be negative."
                raise SnaptimeError(msg)
            if self.unit is None:
                msg = "Snaptime string is invalid: missing time unit for time addition or subtraction."
                raise SnaptimeError(msg)
