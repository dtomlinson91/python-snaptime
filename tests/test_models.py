import re
from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta

import pytest
from python_snaptime.models import Action, Snaptime, Unit, Weekday


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


@pytest.mark.parametrize("day", range(7))
def test_weekday_matches_datetime_weekday(day: int):
    # arrange
    dtm = datetime(2024, 12, 30) + timedelta(days=day)

    # act/assert
    assert Weekday(dtm.weekday()).name == dtm.strftime("%A").upper()


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

    @pytest.mark.parametrize(
        "unit,time_int",
        [("s", 1), ("s", 30), ("m", 1), ("m", 15), ("m", 60), ("h", 1), ("h", 6), ("h", 24), (Unit.MINUTE, 15)],
    )
    def test_snaptime_verify_snap_multiple(self, unit, time_int):
        # act
        snaptime = Snaptime(action="@", unit=unit, time_int=time_int)

        # assert
        assert snaptime.time_int == time_int

    @pytest.mark.parametrize("unit", ["d", "w", "mon", "q", "y", Unit.DAY])
    def test_snaptime_verify_snap_multiple_unit(self, unit):
        # arrange
        snaptime = {"action": "@", "unit": unit, "time_int": 2}

        # act/assert
        with pytest.raises(
            ValueError,
            match=re.escape("Snaptime string is invalid: can only snap to a multiple of seconds, minutes or hours."),
        ):
            Snaptime(**snaptime)

    @pytest.mark.parametrize(
        "unit,time_int,limit",
        [("s", 7, 60), ("m", 7, 60), ("m", 0, 60), ("m", -15, 60), ("m", 120, 60), ("h", 5, 24), ("h", 48, 24)],
    )
    def test_snaptime_verify_snap_multiple_divisor(self, unit, time_int, limit):
        # arrange
        snaptime = {"action": "@", "unit": unit, "time_int": time_int}

        # act/assert
        with pytest.raises(
            ValueError,
            match=re.escape(
                f"Snaptime string is invalid: a snap multiple must divide {limit}, but {time_int} does not."
            ),
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

    @pytest.mark.parametrize(
        "snaptime,action,unit,time_int",
        [
            ({"action": "@", "unit": "d"}, Action.SNAP, Unit.DAY, None),
            ({"action": "+", "unit": "hours", "time_int": 2}, Action.ADD, Unit.HOUR, 2),
            ({"action": "-", "unit": "mon", "time_int": 3}, Action.SUB, Unit.MONTH, 3),
            ({"action": Action.SNAP, "unit": Unit.WEEK}, Action.SNAP, Unit.WEEK, None),
        ],
    )
    def test_snaptime_converts_strings_to_enums(self, snaptime, action, unit, time_int):
        # act
        result = Snaptime(**snaptime)

        # assert
        assert result.action is action
        assert result.unit is unit
        assert result.time_int == time_int

    @pytest.mark.parametrize("unit,name", [(Unit.MILLISECOND, "millisecond"), (Unit.MICROSECOND, "microsecond")])
    def test_snaptime_verify_snap_unit_enum_subsecond(self, unit, name):
        # act/assert
        with pytest.raises(ValueError, match=re.escape(f"Snaptime string is invalid: cannot snap to nearest {name}.")):
            Snaptime(action=Action.SNAP, unit=unit)

    def test_snaptime_invalid_action(self):
        # act/assert
        with pytest.raises(ValueError, match=re.escape("'@@' is not a valid Action")):
            Snaptime(action="@@", unit="d")

    def test_snaptime_invalid_unit(self):
        # act/assert
        with pytest.raises(ValueError, match=re.escape("'xyz' is not a valid Unit")):
            Snaptime(action="@", unit="xyz")

    def test_snaptime_equality_and_hash(self):
        # arrange
        first = Snaptime(action="-", unit="h", time_int=2)
        second = Snaptime(action=Action.SUB, unit=Unit.HOUR, time_int=2)

        # act/assert
        assert first == second
        assert hash(first) == hash(second)
        assert first != Snaptime(action="+", unit="h", time_int=2)

    def test_snaptime_repr(self):
        # act
        result = repr(Snaptime(action="@", unit="d"))

        # assert
        assert result == "Snaptime(action=<Action.SNAP: '@'>, unit=<Unit.DAY: ('d', 'day', 'days')>, time_int=None)"

    def test_snaptime_is_frozen(self):
        # arrange
        snaptime = Snaptime(action="@", unit="d")

        # act/assert
        with pytest.raises(FrozenInstanceError):
            snaptime.unit = Unit.HOUR

    def test_snaptime_is_keyword_only(self):
        # act/assert
        with pytest.raises(TypeError):
            Snaptime("@", "d")

    @pytest.mark.parametrize(
        "snaptime",
        [{"action": "+", "unit": "h", "time_int": -2}, {"action": "-", "unit": "h", "time_int": -2}],
    )
    def test_snaptime_verify_delta_negative_time_int(self, snaptime):
        # act/assert
        with pytest.raises(ValueError, match=re.escape("Snaptime string is invalid: time integer cannot be negative.")):
            Snaptime(**snaptime)

    def test_snaptime_verify_delta_zero_time_int(self):
        # act
        snaptime = Snaptime(action="+", unit="h", time_int=0)

        # assert
        assert snaptime.time_int == 0


@pytest.mark.parametrize(
    "unit,result",
    [
        (Unit.MICROSECOND, "+3us"),
        (Unit.MILLISECOND, "+3ms"),
        (Unit.SECOND, "+3s"),
        (Unit.MINUTE, "+3m"),
        (Unit.HOUR, "+3h"),
        (Unit.DAY, "+3d"),
        (Unit.WEEK, "+3w"),
        (Unit.MONTH, "+3mon"),
        (Unit.QUARTER, "+3q"),
        (Unit.YEAR, "+3y"),
    ],
)
def test_snaptime_str_unit(unit, result):
    # arrange
    snaptime = Snaptime(action=Action.ADD, unit=unit, time_int=3)

    # act
    snaptime_str = str(snaptime)

    # assert
    assert snaptime_str == result


@pytest.mark.parametrize(
    "snaptime,result",
    [
        (Snaptime(action=Action.SNAP, unit=Unit.DAY), "@d"),
        (Snaptime(action=Action.ADD, unit=Unit.HOUR, time_int=2), "+2h"),
        (Snaptime(action=Action.SUB, unit=Unit.HOUR, time_int=2), "-2h"),
        (Snaptime(action="-", unit="hours", time_int=6), "-6h"),
        (Snaptime(action=Action.SNAP, unit=Unit.MINUTE, time_int=15), "@15m"),
        (Snaptime(action="@", unit="seconds", time_int=30), "@30s"),
        (Snaptime(action="@", unit="hr", time_int=1), "@1h"),
    ],
)
def test_snaptime_str_action(snaptime, result):
    # act
    snaptime_str = str(snaptime)

    # assert
    assert snaptime_str == result
