import re

import pytest

from python_snaptime.models import Snaptime, Unit


@pytest.mark.parametrize(
    "unit,result",
    [
        ("us", Unit.MICROSECOND),
        ("microsecond", Unit.MICROSECOND),
        ("microseconds", Unit.MICROSECOND),
        ("ms", Unit.MILLISECOND),
        ("millisecond", Unit.MILLISECOND),
        ("milliseconds", Unit.MILLISECOND),
        ("s", Unit.SECOND),
        ("sec", Unit.SECOND),
        ("secs", Unit.SECOND),
        ("second", Unit.SECOND),
        ("seconds", Unit.SECOND),
        ("m", Unit.MINUTE),
        ("min", Unit.MINUTE),
        ("mins", Unit.MINUTE),
        ("minute", Unit.MINUTE),
        ("minutes", Unit.MINUTE),
        ("h", Unit.HOUR),
        ("hr", Unit.HOUR),
        ("hrs", Unit.HOUR),
        ("hour", Unit.HOUR),
        ("hours", Unit.HOUR),
        ("d", Unit.DAY),
        ("day", Unit.DAY),
        ("days", Unit.DAY),
        ("w", Unit.WEEK),
        ("week", Unit.WEEK),
        ("weeks", Unit.WEEK),
        ("mon", Unit.MONTH),
        ("month", Unit.MONTH),
        ("months", Unit.MONTH),
        ("q", Unit.QUARTER),
        ("qtr", Unit.QUARTER),
        ("qtrs", Unit.QUARTER),
        ("quarter", Unit.QUARTER),
        ("quarters", Unit.QUARTER),
        ("y", Unit.YEAR),
        ("yr", Unit.YEAR),
        ("yrs", Unit.YEAR),
        ("year", Unit.YEAR),
        ("years", Unit.YEAR),
    ],
)
def test_microseconds(unit, result):
    # act
    unit_result = Unit(unit)

    # assert
    assert unit_result == result


class TestSnaptime:
    def test_snaptime_verify_no_action(self):
        # arrange
        snaptime = {"unit": "day", "time_int": 2}

        # act/assert
        with pytest.raises(
            ValueError,
            match=re.escape("Snaptime string is invalid: must provide either a snap `@` or time delta `+-`."),
        ):
            Snaptime(**snaptime)

    def test_snaptime_verify_snap_no_time_int(self):
        # arrange
        snaptime = {"action": "@", "time_int": 2}

        # act/assert
        with pytest.raises(
            ValueError, match=re.escape("Snaptime string is invalid: cannot use a time integer when snapping.")
        ):
            Snaptime(**snaptime)

    def test_snaptime_verify_snap_no_unit(self):
        # arrange
        snaptime = {"action": "@", "unit": None}

        # act/assert
        with pytest.raises(ValueError, match=re.escape("Snaptime string is invalid: missing time unit when snapping.")):
            Snaptime(**snaptime)

    def test_snaptime_verify_snap_unit_millisecond(self):
        # arrange
        snaptime = {"action": "@", "unit": "ms"}

        # act/assert
        with pytest.raises(
            ValueError, match=re.escape("Snaptime string is invalid: cannot snap to nearest millisecond.")
        ):
            Snaptime(**snaptime)

    def test_snaptime_verify_snap_unit_microsecond(self):
        # arrange
        snaptime = {"action": "@", "unit": "us"}

        # act/assert
        with pytest.raises(
            ValueError, match=re.escape("Snaptime string is invalid: cannot snap to nearest microsecond.")
        ):
            Snaptime(**snaptime)

    @pytest.mark.parametrize("snaptime", [{"action": "+", "unit": "day"}, {"action": "-", "unit": "day"}])
    def test_snaptime_verify_delta_no_time_int(self, snaptime):
        # act/assert
        with pytest.raises(
            ValueError,
            match=re.escape("Snaptime string is invalid: missing time integer for time addition or subtraction."),
        ):
            Snaptime(**snaptime)

    @pytest.mark.parametrize("snaptime", [{"action": "+", "time_int": 2}, {"action": "-", "time_int": 2}])
    def test_snaptime_verify_delta_no_unit(self, snaptime):
        # act/assert
        with pytest.raises(
            ValueError,
            match=re.escape("Snaptime string is invalid: missing time unit for time addition or subtraction."),
        ):
            Snaptime(**snaptime)
