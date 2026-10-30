import re
from datetime import datetime, timezone

import pendulum
import pytest
import python_snaptime
from python_snaptime import Snaptime, SnaptimeError, compile, parse, snap, snap_range

INVALID_SNAPTIMES = [
    ("", "Snaptime string is invalid"),
    ("@d!", "Snaptime string is invalid: unknown character `!`."),
    ("2d", "Snaptime string is invalid: must provide either a snap `@` or time delta `+-`."),
    ("@2d", "Snaptime string is invalid: can only snap to a multiple of seconds, minutes or hours."),
    ("@7m", "Snaptime string is invalid: a snap multiple must divide 60, but 7 does not."),
    ("@", "Snaptime string is invalid: missing time unit when snapping."),
    ("@ms", "Snaptime string is invalid: cannot snap to nearest millisecond."),
    ("@us", "Snaptime string is invalid: cannot snap to nearest microsecond."),
    ("+d", "Snaptime string is invalid: missing time integer for time addition or subtraction."),
    ("-2", "Snaptime string is invalid: missing time unit for time addition or subtraction."),
    ("@@d", "'@@' is not a valid Action"),
    ("@xyz", "'xyz' is not a valid Unit"),
]


@pytest.fixture(
    params=[
        pendulum.datetime(2024, 12, 30, 18, 52, tz="Europe/London"),
        datetime(2024, 12, 30, 18, 52, tzinfo=timezone.utc),
    ],
    ids=["pendulum", "datetime"],
)
def dtm(request):
    return request.param


def test_snaptime_error_is_value_error():
    # act/assert
    assert issubclass(SnaptimeError, ValueError)


def test_snaptime_error_is_exported():
    # act/assert
    assert "SnaptimeError" in python_snaptime.__all__


@pytest.mark.parametrize("snaptime,message", INVALID_SNAPTIMES)
def test_snap_raises_snaptime_error(dtm, snaptime, message):
    # act/assert
    with pytest.raises(SnaptimeError, match=f"^{re.escape(message)}$"):
        snap(dtm, snaptime)


@pytest.mark.parametrize("snaptime,message", INVALID_SNAPTIMES)
@pytest.mark.parametrize("function", [parse, compile])
def test_parse_raises_snaptime_error(function, snaptime, message):
    # act/assert
    with pytest.raises(SnaptimeError, match=f"^{re.escape(message)}$"):
        function(snaptime)


@pytest.mark.parametrize("snaptime,message", INVALID_SNAPTIMES)
@pytest.mark.parametrize("inclusive", [False, True])
def test_snap_range_invalid_snaptime_raises_snaptime_error(dtm, snaptime, message, inclusive):
    # act/assert
    with pytest.raises(SnaptimeError, match=f"^{re.escape(message)}$"):
        snap_range(dtm, "@d", snaptime, inclusive=inclusive)


@pytest.mark.parametrize("inclusive", [False, True])
def test_snap_range_reversed_raises_snaptime_error(dtm, inclusive):
    # act/assert
    with pytest.raises(SnaptimeError, match=re.escape("The start of the range ('@d') is after the end ('-1d@d').")):
        snap_range(dtm, "@d", "-1d@d", inclusive=inclusive)


def test_snap_range_empty_inclusive_raises_snaptime_error(dtm):
    # act/assert
    with pytest.raises(
        SnaptimeError, match=re.escape("The range from '@d' to '@d' is empty. An inclusive range must not be empty.")
    ):
        snap_range(dtm, "@d", "@d", inclusive=True)


@pytest.mark.parametrize("error", [SnaptimeError, ValueError])
def test_snap_invalid_snaptime_caught_as_both_errors(dtm, error):
    # act/assert
    with pytest.raises(error):
        snap(dtm, "@ms")


@pytest.mark.parametrize(
    "snaptime,message",
    [
        ({"action": "@@", "unit": "d"}, "'@@' is not a valid Action"),
        ({"action": "@", "unit": "xyz"}, "'xyz' is not a valid Unit"),
    ],
)
def test_snaptime_invalid_enum_raises_snaptime_error(snaptime, message):
    # act
    with pytest.raises(SnaptimeError, match=f"^{re.escape(message)}$") as exc_info:
        Snaptime(**snaptime)

    # assert
    assert type(exc_info.value.__cause__) is ValueError


@pytest.mark.parametrize(
    "snaptime,message",
    [
        ({"action": "+", "unit": "h", "time_int": -2}, "Snaptime string is invalid: time integer cannot be negative."),
        (
            {"action": "@", "unit": "m", "time_int": -15},
            "Snaptime string is invalid: a snap multiple must divide 60, but -15 does not.",
        ),
    ],
)
def test_snaptime_invalid_time_int_raises_snaptime_error(snaptime, message):
    # act/assert
    with pytest.raises(SnaptimeError, match=f"^{re.escape(message)}$"):
        Snaptime(**snaptime)
