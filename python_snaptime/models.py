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


# TODO: test each unit
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

    @model_validator(mode="before")
    @classmethod
    def _verify_model(cls, values: SnaptimeDict) -> SnaptimeDict:
        action = values.get("action")
        unit = values.get("unit")
        time_int = values.get("time_int")

        if action is None:
            raise ValueError("Snaptime string is invalid: must provide either a snap `@` or time delta `+-`.")

        if action == Action.SNAP:
            if time_int is not None:
                raise ValueError("Snaptime string is invalid: cannot use a time integer when snapping.")
            if unit is None:
                raise ValueError("Snaptime string is invalid: missing time unit when snapping.")
            if unit in Unit.MILLISECOND.value:
                raise ValueError("Snaptime string is invalid: cannot snap to nearest millisecond.")
            if unit in Unit.MICROSECOND.value:
                raise ValueError("Snaptime string is invalid: cannot snap to nearest microsecond.")
        elif action in (Action.ADD, Action.SUB):
            if time_int is None:
                raise ValueError("Snaptime string is invalid: missing time integer for time addition or subtraction.")
            if unit is None:
                raise ValueError("Snaptime string is invalid: missing time unit for time addition or subtraction.")
        return values
