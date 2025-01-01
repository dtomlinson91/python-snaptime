"""Module to handle the snaptime cases."""

import pendulum

from python_snaptime.models import Action, Snaptime, Unit


def _handle_snap_cases(snap: Snaptime, dtm: pendulum.DateTime) -> pendulum.DateTime:
    if snap.time_int is not None:
        raise ValueError("Time integer is not allowed for SNAP action.")
    if snap.unit == Unit.SECOND:
        dtm = dtm.start_of("second")
    elif snap.unit == Unit.MINUTE:
        dtm = dtm.start_of("minute")
    elif snap.unit == Unit.HOUR:
        dtm = dtm.start_of("hour")
    elif snap.unit == Unit.DAY:
        dtm = dtm.start_of("day")
    elif snap.unit == Unit.WEEK:
        dtm = dtm.start_of("week")
    elif snap.unit == Unit.MONTH:
        dtm = dtm.start_of("month")
    elif snap.unit == Unit.QUARTER:
        month = (((dtm.month - 1) // 3) * 3) + 1
        dtm = dtm.set(month=month, day=1, hour=0, minute=0, second=0, microsecond=0)
    elif snap.unit == Unit.YEAR:
        dtm = dtm.start_of("year")
    return dtm


def _handle_addition_cases(snap: Snaptime, dtm: pendulum.DateTime) -> pendulum.DateTime:
    if snap.time_int is None:
        raise ValueError("Time integer is required for ADD action.")
    if snap.unit == Unit.MICROSECOND:
        dtm = dtm.add(microseconds=snap.time_int)
    elif snap.unit == Unit.MILLISECOND:
        dtm = dtm.add(microseconds=snap.time_int * 1000)
    elif snap.unit == Unit.SECOND:
        dtm = dtm.add(seconds=snap.time_int)
    elif snap.unit == Unit.MINUTE:
        dtm = dtm.add(minutes=snap.time_int)
    elif snap.unit == Unit.HOUR:
        dtm = dtm.add(hours=snap.time_int)
    elif snap.unit == Unit.DAY:
        dtm = dtm.add(days=snap.time_int)
    elif snap.unit == Unit.WEEK:
        dtm = dtm.add(weeks=snap.time_int)
    elif snap.unit == Unit.MONTH:
        dtm = dtm.add(months=snap.time_int)
    elif snap.unit == Unit.QUARTER:
        dtm = dtm.add(months=snap.time_int * 3)
    elif snap.unit == Unit.YEAR:
        dtm = dtm.add(years=snap.time_int)
    return dtm


def _handle_subtraction_cases(snap: Snaptime, dtm: pendulum.DateTime) -> pendulum.DateTime:
    if snap.time_int is None:
        raise ValueError("Time integer is required for SUB action.")
    if snap.unit == Unit.MICROSECOND:
        dtm = dtm.subtract(microseconds=snap.time_int)
    elif snap.unit == Unit.MILLISECOND:
        dtm = dtm.subtract(microseconds=snap.time_int * 1000)
    elif snap.unit == Unit.SECOND:
        dtm = dtm.subtract(seconds=snap.time_int)
    elif snap.unit == Unit.MINUTE:
        dtm = dtm.subtract(minutes=snap.time_int)
    elif snap.unit == Unit.HOUR:
        dtm = dtm.subtract(hours=snap.time_int)
    elif snap.unit == Unit.DAY:
        dtm = dtm.subtract(days=snap.time_int)
    elif snap.unit == Unit.WEEK:
        dtm = dtm.subtract(weeks=snap.time_int)
    elif snap.unit == Unit.MONTH:
        dtm = dtm.subtract(months=snap.time_int)
    elif snap.unit == Unit.QUARTER:
        dtm = dtm.subtract(months=snap.time_int * 3)
    elif snap.unit == Unit.YEAR:
        dtm = dtm.subtract(years=snap.time_int)
    return dtm


def _handle_delta_cases(snap: Snaptime, dtm: pendulum.DateTime) -> pendulum.DateTime:
    if snap.action == Action.ADD:
        dtm = _handle_addition_cases(snap, dtm)
    elif snap.action == Action.SUB:
        dtm = _handle_subtraction_cases(snap, dtm)
    return dtm


def handle_timesnapping(snap: Snaptime, dtm: pendulum.DateTime) -> pendulum.DateTime:
    """Handle different time snapping cases using the snaptime action.

    Args:
        snap (Snaptime): An instance of `Snaptime` containing the time snapping to be performed.
        dtm (pendulum.DateTime): The datetime object to apply to the time snapping.

    Returns:
        pendulum.DateTime: The resulting datetime object after applying the time snapping.
    """
    if snap.action == Action.SNAP:
        dtm = _handle_snap_cases(snap, dtm)
    if snap.action in (Action.ADD, Action.SUB):
        dtm = _handle_delta_cases(snap, dtm)
    return dtm
