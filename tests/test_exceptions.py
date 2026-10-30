import re
from datetime import datetime, timezone

import pendulum
import pytest
import python_snaptime
from python_snaptime import Snaptime, SnaptimeError, snap
from python_snaptime.parsers import _parse_raw_snaptime

INVALID_SNAPTIMES = [
    ("", "Snaptime string is invalid"),
    ("@d!", "Snaptime string is invalid: unknown character `!`."),
    ("2d", "Snaptime string is invalid: must provide either a snap `@` or time delta `+-`."),
    ("@2d", "Snaptime string is invalid: cannot use a time integer when snapping."),
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
def test_parse_raw_snaptime_raises_snaptime_error(snaptime, message):
    # act/assert
    with pytest.raises(SnaptimeError, match=f"^{re.escape(message)}$"):
        _parse_raw_snaptime(snaptime)


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
