import re

import pendulum
import pytest
import python_snaptime
from pytest_mock import MockerFixture
from python_snaptime import parsers
from python_snaptime.exceptions import SnaptimeError
from python_snaptime.models import Action, Snaptime, Unit, Weekday
from python_snaptime.parsers import NOW, is_valid, parse, parse_snaptime_string, to_string


class TestParse:
    def test_parse_valid(self):
        # arrange
        snaptime = "@d-2h+10m"
        snap_results = [
            Snaptime(action=Action.SNAP, unit=Unit.DAY),
            Snaptime(action=Action.SUB, unit=Unit.HOUR, time_int=2),
            Snaptime(action=Action.ADD, unit=Unit.MINUTE, time_int=10),
        ]

        # act
        results = parse(snaptime)

        # assert
        assert results == snap_results

    def test_parse_snap_multiple(self):
        # act
        results = parse("@15m")

        # assert
        assert results == [Snaptime(action=Action.SNAP, unit=Unit.MINUTE, time_int=15)]

    @pytest.mark.parametrize(
        "snaptime,weekday",
        [
            ("@w0", Weekday.SUNDAY),
            ("@w1", Weekday.MONDAY),
            ("@w2", Weekday.TUESDAY),
            ("@w3", Weekday.WEDNESDAY),
            ("@w4", Weekday.THURSDAY),
            ("@w5", Weekday.FRIDAY),
            ("@w6", Weekday.SATURDAY),
            ("@w7", Weekday.SUNDAY),
        ],
    )
    def test_parse_weekday(self, snaptime: str, weekday: Weekday):
        # act
        results = parse(snaptime)

        # assert
        assert results == [Snaptime(action=Action.SNAP, unit=Unit.WEEK, weekday=weekday)]

    def test_parse_weekday_chain(self):
        # act
        results = parse("-7d@w1+2h")

        # assert
        assert results == [
            Snaptime(action=Action.SUB, unit=Unit.DAY, time_int=7),
            Snaptime(action=Action.SNAP, unit=Unit.WEEK, weekday=Weekday.MONDAY),
            Snaptime(action=Action.ADD, unit=Unit.HOUR, time_int=2),
        ]

    @pytest.mark.parametrize("snaptime", ["@w", "@week", "@weeks"])
    def test_parse_week_without_weekday(self, snaptime: str):
        # act
        results = parse(snaptime)

        # assert
        assert results == [Snaptime(action=Action.SNAP, unit=Unit.WEEK)]

    def test_parse_invalid(self, mocker):
        # arrange
        snaptime = ""

        # act/assert
        with pytest.raises(ValueError, match="^Snaptime string is invalid$"):
            parse(snaptime)

    @pytest.mark.parametrize(
        "snaptime,character",
        [("@d!", "!"), ("@d -2h", " "), ("@d,-2h", ","), ("@d$$+1h", "$"), ("@d-1.5h", ".")],
    )
    def test_parse_unknown_character(self, snaptime: str, character: str):
        # act/assert
        with pytest.raises(
            ValueError, match=re.escape(f"Snaptime string is invalid: unknown character `{character}`.")
        ):
            parse(snaptime)

    def test_parse_exported_from_package(self):
        # assert
        assert python_snaptime.parse is parse
        assert "parse" in python_snaptime.__all__

    @pytest.mark.parametrize("snaptime", ["now", NOW])
    def test_parse_now(self, snaptime: str):
        # act
        results = parse(snaptime)

        # assert
        assert results == []

    @pytest.mark.parametrize("snaptime", ["now-1d", "-1dnow", "@dnow", "nowx", "now()", "NOW", "Now", "now now"])
    def test_parse_now_not_whole_string(self, snaptime: str):
        # act/assert
        with pytest.raises(
            SnaptimeError,
            match=re.escape("Snaptime string is invalid: `now` must be the whole snaptime string, in lower case."),
        ):
            parse(snaptime)


class TestNow:
    def test_now_value(self):
        # assert
        assert NOW == "now"

    def test_now_exported_from_package(self):
        # assert
        assert python_snaptime.NOW is NOW
        assert "NOW" in python_snaptime.__all__


class TestIsValid:
    @pytest.mark.parametrize(
        "snaptime",
        ["@d", "@d-2h", "@d-2h+10m", "-6hours", "@15m", "+0h", "-1d@d+1y@y-2sec@s", "now", NOW, "@w0", "@w7", "-7d@w1"],
    )
    def test_is_valid_true(self, snaptime: str):
        # act/assert
        assert is_valid(snaptime) is True

    @pytest.mark.parametrize(
        "snaptime",
        ["", "@d -2h", "@d!", "@d,-2h", "@d-1.5h", "@d\n", "now-1d", "@dnow", "NOW", "now()", "@w8", "+w5"],
    )
    def test_is_valid_false(self, snaptime: str):
        # act/assert
        assert is_valid(snaptime) is False

    def test_is_valid_raises_other_errors(self, mocker: MockerFixture):
        # arrange
        mocker.patch.object(parsers, "parse", side_effect=ValueError("not a snaptime error"))

        # act/assert
        with pytest.raises(ValueError, match="^not a snaptime error$"):
            is_valid("@d")

    def test_is_valid_exported_from_package(self):
        # assert
        assert python_snaptime.is_valid is is_valid
        assert "is_valid" in python_snaptime.__all__


def test_parse_snaptime_string(mocker: MockerFixture):
    # arrange
    dtm = pendulum.datetime(2024, 12, 30, 13, 1, 10, 999999)
    dtm_snap = pendulum.datetime(2024, 12, 29, 22, 10, 0, 000000)
    snaptime = "@d-2h+10m"
    call_args = [
        (
            Snaptime(action=Action.SNAP, unit=Unit.DAY),
            pendulum.datetime(2024, 12, 30, 13, 1, 10, 999999),
        ),
        (
            Snaptime(action=Action.SUB, unit=Unit.HOUR, time_int=2),
            pendulum.datetime(2024, 12, 30, 0, 0, 0, 000000),
        ),
        (
            Snaptime(action=Action.ADD, unit=Unit.MINUTE, time_int=10),
            pendulum.datetime(2024, 12, 29, 22, 0, 0),
        ),
    ]
    return_values = [
        pendulum.datetime(2024, 12, 30, 0, 0, 0, 000000),
        pendulum.datetime(2024, 12, 29, 22, 0, 0),
        pendulum.datetime(2024, 12, 29, 22, 10, 0),
    ]

    mock_handle_timesnapping = mocker.patch.object(parsers, "handle_timesnapping")
    mock_handle_timesnapping.side_effect = return_values

    # act
    result = parse_snaptime_string(snaptime, dtm)

    # assert
    assert mock_handle_timesnapping.call_count == 3
    assert [arg.args for arg in mock_handle_timesnapping.call_args_list] == call_args
    assert result == dtm_snap


class TestToString:
    def test_to_string(self):
        # arrange
        snaptimes = [
            Snaptime(action=Action.SNAP, unit=Unit.DAY),
            Snaptime(action=Action.SUB, unit=Unit.HOUR, time_int=2),
            Snaptime(action=Action.ADD, unit=Unit.MINUTE, time_int=10),
        ]

        # act
        result = to_string(snaptimes)

        # assert
        assert result == "@d-2h+10m"

    def test_to_string_iterable(self):
        # arrange
        snaptimes = (snaptime for snaptime in [Snaptime(action=Action.SNAP, unit=Unit.MONTH)])

        # act
        result = to_string(snaptimes)

        # assert
        assert result == "@mon"

    def test_to_string_empty(self):
        # act
        result = to_string([])

        # assert
        assert result == "now"
        assert result == NOW

    @pytest.mark.parametrize(
        "snaptime,result",
        [
            ("@d-2h+10m", "@d-2h+10m"),
            ("-6hours", "-6h"),
            ("@mon+1month-3minutes", "@mon+1mon-3m"),
            ("@q-1qtr@w+500ms+10us", "@q-1q@w+500ms+10us"),
            ("-1d@d+1y@y-2sec@s", "-1d@d+1y@y-2s@s"),
            ("@15m", "@15m"),
            ("@d-2h@15minutes", "@d-2h@15m"),
            ("@30sec+1h@2hours", "@30s+1h@2h"),
            ("now", "now"),
            ("@w5", "@w5"),
            ("@w0", "@w0"),
            ("@w7", "@w0"),
            ("-7d@w1+2h", "-7d@w1+2h"),
            ("@weeks@w6", "@w@w6"),
        ],
    )
    def test_to_string_round_trip(self, snaptime: str, result: str):
        # arrange
        snaptimes = parse(snaptime)

        # act
        snaptime_str = to_string(snaptimes)

        # assert
        assert snaptime_str == result
        assert parse(snaptime_str) == snaptimes
