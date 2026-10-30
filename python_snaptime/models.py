"""Module defining models for python-snaptime."""

from __future__ import annotations

from enum import Enum
from typing import TypedDict

from pydantic import BaseModel, field_validator, model_validator


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

    def __str__(self) -> str:
        """Return the snaptime string of this snaptime, for example `@d` or `-2h`.

        Returns:
            str: The snaptime string, with the shortest string of the unit.
        """
        action = self.action.value if self.action is not None else ""
        time_int = str(self.time_int) if self.time_int is not None else ""
        unit = self.unit.value[0] if self.unit is not None else ""
        return f"{action}{time_int}{unit}"

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
            if time_int is not None:
                msg = "Snaptime string is invalid: cannot use a time integer when snapping."
                raise ValueError(msg)
            if unit is None:
                msg = "Snaptime string is invalid: missing time unit when snapping."
                raise ValueError(msg)
            if unit in Unit.MILLISECOND.value:
                msg = "Snaptime string is invalid: cannot snap to nearest millisecond."
                raise ValueError(msg)
            if unit in Unit.MICROSECOND.value:
                msg = "Snaptime string is invalid: cannot snap to nearest microsecond."
                raise ValueError(msg)
        elif action in (Action.ADD, Action.SUB):
            if time_int is None:
                msg = "Snaptime string is invalid: missing time integer for time addition or subtraction."
                raise ValueError(msg)
            if unit is None:
                msg = "Snaptime string is invalid: missing time unit for time addition or subtraction."
                raise ValueError(msg)
        return values

    @field_validator("time_int")
    @classmethod
    def _verify_time_int(cls, time_int: int | None) -> int | None:
        if time_int is not None and time_int < 0:
            msg = "Snaptime string is invalid: time integer cannot be negative."
            raise ValueError(msg)
        return time_int
