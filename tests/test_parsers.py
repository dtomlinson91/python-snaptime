import pendulum
import pytest
from pytest_mock import MockerFixture

from python_snaptime.models import Action, Snaptime, Unit
from python_snaptime import parsers
from python_snaptime.parsers import _parse_raw_snaptime, parse_snaptime_string


class TestParseRawSnaptime:
    def test_parse_raw_snaptime_valid(self):
        # arrange
        snaptime = "@d-2h+10m"
        snap_results = [
            Snaptime(action=Action.SNAP, unit=Unit.DAY),
            Snaptime(action=Action.SUB, unit=Unit.HOUR, time_int=2),
            Snaptime(action=Action.ADD, unit=Unit.MINUTE, time_int=10),
        ]

        # act
        results = _parse_raw_snaptime(snaptime)

        # assert
        assert results == snap_results

    def test_parse_raw_snaptime_invalid(self, mocker):
        # arrange
        snaptime = ""

        # act/assert
        with pytest.raises(ValueError, match="^Snaptime string is invalid$"):
            _parse_raw_snaptime(snaptime)


def test_parse_snaptime_string(mocker: MockerFixture):
    # arrange
    dtm = pendulum.datetime(2024, 12, 30, 13, 1, 10, 999999)
    dtm_snap = pendulum.datetime(2024, 12, 29, 22, 10, 0, 000000)
    snaptime = "@d-2h+10m"

    mock_handle_cases = mocker.patch.object(parsers, "handle_cases")
    mock_handle_cases.return_value = dtm_snap

    # act
    result = parse_snaptime_string(snaptime, dtm)

    # assert
    assert mock_handle_cases.call_count == 3
    assert result == dtm_snap