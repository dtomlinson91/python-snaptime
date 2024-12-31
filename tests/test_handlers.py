import pytest
import pendulum
from python_snaptime.handlers import _handle_snap_cases
from python_snaptime.models import Action, Snaptime, Unit


def test_handle_snap_cases_second():
    snap = Snaptime(action=Action.SNAP, unit=Unit.SECOND, time_int=None)
    dtm = pendulum.datetime(2024, 12, 30, 13, 1, 10, 999999)
    result = _handle_snap_cases(snap, dtm)
    assert result == pendulum.datetime(2024, 12, 30, 13, 1, 10, 000000)


def test_handle_snap_cases_minute():
    snap = Snaptime(action=Action.SNAP, unit=Unit.MINUTE, time_int=None)
    dtm = pendulum.datetime(2024, 12, 30, 13, 1, 10, 999999)
    result = _handle_snap_cases(snap, dtm)
    assert result == pendulum.datetime(2024, 12, 30, 13, 1, 0, 000000)


def test_handle_snap_cases_hour():
    snap = Snaptime(action=Action.SNAP, unit=Unit.HOUR, time_int=None)
    dtm = pendulum.datetime(2024, 12, 30, 13, 1, 10, 999999)
    result = _handle_snap_cases(snap, dtm)
    assert result == pendulum.datetime(2024, 12, 30, 13, 0, 0, 000000)


def test_handle_snap_cases_day():
    snap = Snaptime(action=Action.SNAP, unit=Unit.DAY, time_int=None)
    dtm = pendulum.datetime(2024, 12, 30, 13, 1, 10, 999999)
    result = _handle_snap_cases(snap, dtm)
    assert result == pendulum.datetime(2024, 12, 30, 0, 0, 0, 000000)


def test_handle_snap_cases_week():
    snap = Snaptime(action=Action.SNAP, unit=Unit.WEEK, time_int=None)
    dtm = pendulum.datetime(2024, 12, 31, 13, 1, 10, 999999)
    result = _handle_snap_cases(snap, dtm)
    assert result == pendulum.datetime(2024, 12, 30, 0, 0, 0, 000000)


def test_handle_snap_cases_month():
    snap = Snaptime(action=Action.SNAP, unit=Unit.MONTH, time_int=None)
    dtm = pendulum.datetime(2024, 12, 30, 13, 1, 10, 999999)
    result = _handle_snap_cases(snap, dtm)
    assert result == pendulum.datetime(2024, 12, 1, 0, 0, 0, 000000)


def test_handle_snap_cases_quarter():
    snap = Snaptime(action=Action.SNAP, unit=Unit.QUARTER, time_int=None)
    dtm = pendulum.datetime(2024, 12, 30, 13, 1, 10, 999999)
    result = _handle_snap_cases(snap, dtm)
    assert result == pendulum.datetime(2024, 10, 1, 0, 0, 0, 000000)


def test_handle_snap_cases_year():
    snap = Snaptime(action=Action.SNAP, unit=Unit.YEAR, time_int=None)
    dtm = pendulum.datetime(2024, 12, 30, 13, 1, 10, 999999)
    result = _handle_snap_cases(snap, dtm)
    assert result == pendulum.datetime(2024, 1, 1, 0, 0, 0, 000000)


def test_handle_snap_cases_with_time_int():
    snap = Snaptime(action=Action.SNAP, unit=Unit.SECOND, time_int=None)
    snap.time_int = 5
    dtm = pendulum.datetime(2024, 12, 30, 13, 1, 10, 999999)
    with pytest.raises(ValueError, match="Time integer is not allowed for SNAP action."):
        _handle_snap_cases(snap, dtm)
