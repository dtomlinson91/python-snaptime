import re

import pendulum
import pytest
import python_snaptime
from pytest_mock import MockerFixture
from python_snaptime import parsers
from python_snaptime.models import Action, Snaptime, Unit
from python_snaptime.parsers import parse, parse_snaptime_string


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
