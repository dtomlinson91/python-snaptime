"""Module defining models for python-snaptime."""

from __future__ import annotations

from enum import Enum
from typing import TypedDict

from pydantic import BaseModel, model_validator


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


_SNAP_MULTIPLE_LIMITS = {Unit.SECOND: 60, Unit.MINUTE: 60, Unit.HOUR: 24}


def _verify_snap_multiple(unit: str | Unit, time_int: int) -> None:
    limit = _SNAP_MULTIPLE_LIMITS.get(Unit(unit))
    if limit is None:
        msg = "Snaptime string is invalid: can only snap to a multiple of seconds, minutes or hours."
        raise ValueError(msg)
    if time_int < 1 or limit % time_int != 0:
        msg = f"Snaptime string is invalid: a snap multiple must divide {limit}, but {time_int} does not."
        raise ValueError(msg)


class SnaptimeDict(TypedDict, total=False):
    """Dictionary representing a snaptime configuration."""

    action: str | None
    unit: str | None
    time_int: int | None


class Snaptime(BaseModel):
    """Model representing a snaptime configuration."""

    action: Action | None = None
    unit: Unit | None = None
    time_int: int | None = None

    @model_validator(mode="before")
    @classmethod
    def _verify_model(cls, values: SnaptimeDict) -> SnaptimeDict:
        action = values.get("action")
        unit = values.get("unit")
        time_int = values.get("time_int")

        if action is None:
            msg = "Snaptime string is invalid: must provide either a snap `@` or time delta `+-`."
            raise ValueError(msg)

        if action == Action.SNAP:
            if unit is None:
                msg = "Snaptime string is invalid: missing time unit when snapping."
                raise ValueError(msg)
            if unit in Unit.MILLISECOND.value:
                msg = "Snaptime string is invalid: cannot snap to nearest millisecond."
                raise ValueError(msg)
            if unit in Unit.MICROSECOND.value:
                msg = "Snaptime string is invalid: cannot snap to nearest microsecond."
                raise ValueError(msg)
            if time_int is not None:
                _verify_snap_multiple(unit, time_int)
        elif action in (Action.ADD, Action.SUB):
            if time_int is None:
                msg = "Snaptime string is invalid: missing time integer for time addition or subtraction."
                raise ValueError(msg)
            if unit is None:
                msg = "Snaptime string is invalid: missing time unit for time addition or subtraction."
                raise ValueError(msg)
        return values
