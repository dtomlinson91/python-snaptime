import pendulum
import pytest
from pytest_mock import MockerFixture
from python_snaptime import handlers
from python_snaptime.models import Action, Snaptime, Unit, Weekday


class TestSnapCases:
    @pytest.fixture()
    def start_time(self):
        return pendulum.datetime(2024, 12, 30, 13, 1, 10, 999999)

    def test_handle_snap_cases_second(self, start_time):
        # arrange
        snap = Snaptime(action=Action.SNAP, unit=Unit.SECOND, time_int=None)

        # act
        result = handlers._handle_snap_cases(snap, start_time)

        # assert
        assert result == pendulum.datetime(2024, 12, 30, 13, 1, 10, 000000)

    def test_handle_snap_cases_minute(self, start_time):
        # arrange
        snap = Snaptime(action=Action.SNAP, unit=Unit.MINUTE, time_int=None)

        # act
        result = handlers._handle_snap_cases(snap, start_time)

        # assert
        assert result == pendulum.datetime(2024, 12, 30, 13, 1, 0, 000000)

    def test_handle_snap_cases_hour(self, start_time):
        # arrange
        snap = Snaptime(action=Action.SNAP, unit=Unit.HOUR, time_int=None)

        # act
        result = handlers._handle_snap_cases(snap, start_time)

        # assert
        assert result == pendulum.datetime(2024, 12, 30, 13, 0, 0, 000000)

    def test_handle_snap_cases_day(self, start_time):
        # arrange
        snap = Snaptime(action=Action.SNAP, unit=Unit.DAY, time_int=None)

        # act
        result = handlers._handle_snap_cases(snap, start_time)

        # assert
        assert result == pendulum.datetime(2024, 12, 30, 0, 0, 0, 000000)

    def test_handle_snap_cases_week(self, start_time):
        # arrange
        snap = Snaptime(action=Action.SNAP, unit=Unit.WEEK, time_int=None)

        # act
        result = handlers._handle_snap_cases(snap, start_time)

        # assert
        assert result == pendulum.datetime(2024, 12, 30, 0, 0, 0, 000000)

    @pytest.mark.parametrize(
        "week_start,result_day",
        [
            (Weekday.MONDAY, 30),
            (Weekday.TUESDAY, 24),
            (Weekday.WEDNESDAY, 25),
            (Weekday.THURSDAY, 26),
            (Weekday.FRIDAY, 27),
            (Weekday.SATURDAY, 28),
            (Weekday.SUNDAY, 29),
        ],
    )
    def test_handle_snap_cases_week_start(self, start_time, week_start: Weekday, result_day: int):
        # arrange
        snap = Snaptime(action=Action.SNAP, unit=Unit.WEEK, time_int=None)

        # act
        result = handlers._handle_snap_cases(snap, start_time, week_start)

        # assert
        assert result == pendulum.datetime(2024, 12, result_day, 0, 0, 0, 000000)

    @pytest.mark.parametrize("week_start", list(Weekday))
    def test_handle_snap_cases_week_start_on_first_day(self, week_start: Weekday):
        # arrange
        snap = Snaptime(action=Action.SNAP, unit=Unit.WEEK, time_int=None)
        dtm = pendulum.datetime(2024, 12, 30, 13, 1, 10, 999999).add(days=week_start)

        # act
        result = handlers._handle_snap_cases(snap, dtm, week_start)

        # assert
        assert result.weekday() == week_start
        assert result == dtm.start_of("day")

    def test_handle_snap_cases_month(self, start_time):
        # arrange
        snap = Snaptime(action=Action.SNAP, unit=Unit.MONTH, time_int=None)

        # act
        result = handlers._handle_snap_cases(snap, start_time)

        # assert
        assert result == pendulum.datetime(2024, 12, 1, 0, 0, 0, 000000)

    def test_handle_snap_cases_quarter(self, start_time):
        # arrange
        snap = Snaptime(action=Action.SNAP, unit=Unit.QUARTER, time_int=None)

        # act
        result = handlers._handle_snap_cases(snap, start_time)

        # assert
        assert result == pendulum.datetime(2024, 10, 1, 0, 0, 0, 000000)

    def test_handle_snap_cases_year(self, start_time):
        # arrange
        snap = Snaptime(action=Action.SNAP, unit=Unit.YEAR, time_int=None)

        # act
        result = handlers._handle_snap_cases(snap, start_time)

        # assert
        assert result == pendulum.datetime(2024, 1, 1, 0, 0, 0, 000000)

    def test_handle_snap_cases_with_time_int(self, start_time):
        # arrange
        snap = Snaptime(action=Action.SNAP, unit=Unit.SECOND, time_int=None)
        object.__setattr__(snap, "time_int", 5)

        # act/assert
        with pytest.raises(ValueError, match="Time integer is not allowed for SNAP action."):
            handlers._handle_snap_cases(snap, start_time)


class TestAdditionCases:
    @pytest.fixture()
    def start_time(self):
        return pendulum.datetime(2024, 12, 30, 13, 1, 10, 999)

    def test_handle_addition_cases_microsecond(self, start_time):
        # arrange
        snap = Snaptime(action=Action.ADD, unit=Unit.MICROSECOND, time_int=1)

        # act
        result = handlers._handle_addition_cases(snap, start_time)

        # assert
        assert result == pendulum.datetime(2024, 12, 30, 13, 1, 10, 1000)

    def test_handle_addition_cases_millisecond(self, start_time):
        # arrange
        snap = Snaptime(action=Action.ADD, unit=Unit.MILLISECOND, time_int=1)

        # act
        result = handlers._handle_addition_cases(snap, start_time)

        # assert
        assert result == pendulum.datetime(2024, 12, 30, 13, 1, 10, 1999)

    def test_handle_addition_cases_second(self, start_time):
        # arrange
        snap = Snaptime(action=Action.ADD, unit=Unit.SECOND, time_int=10)

        # act
        result = handlers._handle_addition_cases(snap, start_time)

        # assert
        assert result == pendulum.datetime(2024, 12, 30, 13, 1, 20, 999)

    def test_handle_addition_cases_minute(self, start_time):
        # arrange
        snap = Snaptime(action=Action.ADD, unit=Unit.MINUTE, time_int=10)

        # act
        result = handlers._handle_addition_cases(snap, start_time)

        # assert
        assert result == pendulum.datetime(2024, 12, 30, 13, 11, 10, 999)

    def test_handle_addition_cases_hour(self, start_time):
        # arrange
        snap = Snaptime(action=Action.ADD, unit=Unit.HOUR, time_int=2)

        # act
        result = handlers._handle_addition_cases(snap, start_time)

        # assert
        assert result == pendulum.datetime(2024, 12, 30, 15, 1, 10, 999)

    def test_handle_addition_cases_day(self, start_time):
        # arrange
        snap = Snaptime(action=Action.ADD, unit=Unit.DAY, time_int=1)

        # act
        result = handlers._handle_addition_cases(snap, start_time)

        # assert
        assert result == pendulum.datetime(2024, 12, 31, 13, 1, 10, 999)

    def test_handle_addition_cases_week(self, start_time):
        # arrange
        snap = Snaptime(action=Action.ADD, unit=Unit.WEEK, time_int=1)

        # act
        result = handlers._handle_addition_cases(snap, start_time)

        # assert
        assert result == pendulum.datetime(2025, 1, 6, 13, 1, 10, 999)

    def test_handle_addition_cases_month(self, start_time):
        # arrange
        snap = Snaptime(action=Action.ADD, unit=Unit.MONTH, time_int=1)

        # act
        result = handlers._handle_addition_cases(snap, start_time)

        # assert
        assert result == pendulum.datetime(2025, 1, 30, 13, 1, 10, 999)

    def test_handle_addition_cases_quarter(self, start_time):
        # arrange
        snap = Snaptime(action=Action.ADD, unit=Unit.QUARTER, time_int=1)

        # act
        result = handlers._handle_addition_cases(snap, start_time)

        # assert
        assert result == pendulum.datetime(2025, 3, 30, 13, 1, 10, 999)

    def test_handle_addition_cases_year(self, start_time):
        # arrange
        snap = Snaptime(action=Action.ADD, unit=Unit.YEAR, time_int=1)

        # act
        result = handlers._handle_addition_cases(snap, start_time)

        # assert
        assert result == pendulum.datetime(2025, 12, 30, 13, 1, 10, 999)

    def test_handle_addition_cases_without_time_int(self, start_time):
        # arrange
        snap = Snaptime(action=Action.SNAP, unit=Unit.SECOND)
        object.__setattr__(snap, "unit", Unit.SECOND)
        object.__setattr__(snap, "time_int", None)
        object.__setattr__(snap, "action", Action.ADD)

        # act/assert
        with pytest.raises(ValueError, match="Time integer is required for ADD action."):
            handlers._handle_addition_cases(snap, start_time)


class TestSubtractionCases:
    @pytest.fixture()
    def start_time(self):
        return pendulum.datetime(2024, 12, 30, 13, 1, 10, 999)

    def test_handle_subtraction_cases_microsecond(self, start_time):
        # arrange
        snap = Snaptime(action=Action.SUB, unit=Unit.MICROSECOND, time_int=1)

        # act
        result = handlers._handle_subtraction_cases(snap, start_time)

        # assert
        assert result == pendulum.datetime(2024, 12, 30, 13, 1, 10, 998)

    def test_handle_subtraction_cases_millisecond(self, start_time):
        # arrange
        snap = Snaptime(action=Action.SUB, unit=Unit.MILLISECOND, time_int=1)

        # act
        result = handlers._handle_subtraction_cases(snap, start_time)

        # assert
        assert result == pendulum.datetime(2024, 12, 30, 13, 1, 9, 999999)

    def test_handle_subtraction_cases_second(self, start_time):
        # arrange
        snap = Snaptime(action=Action.SUB, unit=Unit.SECOND, time_int=10)

        # act
        result = handlers._handle_subtraction_cases(snap, start_time)

        # assert
        assert result == pendulum.datetime(2024, 12, 30, 13, 1, 0, 999)

    def test_handle_subtraction_cases_minute(self, start_time):
        # arrange
        snap = Snaptime(action=Action.SUB, unit=Unit.MINUTE, time_int=10)

        # act
        result = handlers._handle_subtraction_cases(snap, start_time)

        # assert
        assert result == pendulum.datetime(2024, 12, 30, 12, 51, 10, 999)

    def test_handle_subtraction_cases_hour(self, start_time):
        # arrange
        snap = Snaptime(action=Action.SUB, unit=Unit.HOUR, time_int=2)

        # act
        result = handlers._handle_subtraction_cases(snap, start_time)

        # assert
        assert result == pendulum.datetime(2024, 12, 30, 11, 1, 10, 999)

    def test_handle_subtraction_cases_day(self, start_time):
        # arrange
        snap = Snaptime(action=Action.SUB, unit=Unit.DAY, time_int=1)

        # act
        result = handlers._handle_subtraction_cases(snap, start_time)

        # assert
        assert result == pendulum.datetime(2024, 12, 29, 13, 1, 10, 999)

    def test_handle_subtraction_cases_week(self, start_time):
        # arrange
        snap = Snaptime(action=Action.SUB, unit=Unit.WEEK, time_int=1)

        # act
        result = handlers._handle_subtraction_cases(snap, start_time)

        # assert
        assert result == pendulum.datetime(2024, 12, 23, 13, 1, 10, 999)

    def test_handle_subtraction_cases_month(self, start_time):
        # arrange
        snap = Snaptime(action=Action.SUB, unit=Unit.MONTH, time_int=1)

        # act
        result = handlers._handle_subtraction_cases(snap, start_time)

        # assert
        assert result == pendulum.datetime(2024, 11, 30, 13, 1, 10, 999)

    def test_handle_subtraction_cases_quarter(self, start_time):
        # arrange
        snap = Snaptime(action=Action.SUB, unit=Unit.QUARTER, time_int=1)

        # act
        result = handlers._handle_subtraction_cases(snap, start_time)

        # assert
        assert result == pendulum.datetime(2024, 9, 30, 13, 1, 10, 999)

    def test_handle_subtraction_cases_year(self, start_time):
        # arrange
        snap = Snaptime(action=Action.SUB, unit=Unit.YEAR, time_int=1)

        # act
        result = handlers._handle_subtraction_cases(snap, start_time)

        # assert
        assert result == pendulum.datetime(2023, 12, 30, 13, 1, 10, 999)

    def test_handle_subtraction_cases_without_time_int(self, start_time):
        # arrange
        snap = Snaptime(action=Action.SNAP, unit=Unit.SECOND)
        object.__setattr__(snap, "action", Action.SUB)
        object.__setattr__(snap, "unit", Unit.SECOND)
        object.__setattr__(snap, "time_int", None)

        # act/assert
        with pytest.raises(ValueError, match="Time integer is required for SUB action."):
            handlers._handle_subtraction_cases(snap, start_time)


class TestHandleDeltaCases:
    def test_handle_delta_addition_cases(self, mocker: MockerFixture):
        # arrange
        snap = Snaptime(action=Action.ADD, unit=Unit.SECOND, time_int=10)
        dtm = pendulum.datetime(2024, 12, 30, 13, 1, 10, 999)

        mock_handle_delta_cases = mocker.patch.object(handlers, "_handle_addition_cases")

        # act
        handlers._handle_delta_cases(snap, dtm)

        # assert
        mock_handle_delta_cases.assert_called_once_with(snap, dtm)

    def test_handle_delta_subtraction_cases(self, mocker: MockerFixture):
        # arrange
        snap = Snaptime(action=Action.SUB, unit=Unit.SECOND, time_int=10)
        dtm = pendulum.datetime(2024, 12, 30, 13, 1, 10, 999)

        mock_handle_delta_cases = mocker.patch.object(handlers, "_handle_subtraction_cases")

        # act
        handlers._handle_delta_cases(snap, dtm)

        # assert
        mock_handle_delta_cases.assert_called_once_with(snap, dtm)


class TestHandleCases:
    def test_handle_cases_snap(self, mocker: MockerFixture):
        # arrange
        snap = Snaptime(action=Action.SNAP, unit=Unit.HOUR)
        dtm = pendulum.datetime(2024, 12, 30, 13, 1, 10, 999)

        mock_handle_cases = mocker.patch.object(handlers, "_handle_snap_cases")

        # act
        handlers.handle_timesnapping(snap, dtm)

        # assert
        mock_handle_cases.assert_called_once_with(snap, dtm, Weekday.MONDAY)

    def test_handle_cases_snap_week_start(self, mocker: MockerFixture):
        # arrange
        snap = Snaptime(action=Action.SNAP, unit=Unit.WEEK)
        dtm = pendulum.datetime(2024, 12, 30, 13, 1, 10, 999)

        mock_handle_cases = mocker.patch.object(handlers, "_handle_snap_cases")

        # act
        handlers.handle_timesnapping(snap, dtm, week_start=Weekday.SUNDAY)

        # assert
        mock_handle_cases.assert_called_once_with(snap, dtm, Weekday.SUNDAY)

    def test_handle_cases_delta(self, mocker: MockerFixture):
        # arrange
        snap = Snaptime(action=Action.ADD, unit=Unit.HOUR, time_int=1)
        dtm = pendulum.datetime(2024, 12, 30, 13, 1, 10, 999)

        mock_handle_cases = mocker.patch.object(handlers, "_handle_delta_cases")

        # act
        handlers.handle_timesnapping(snap, dtm)

        # assert
        mock_handle_cases.assert_called_once_with(snap, dtm)
