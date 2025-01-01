import re

import pytest

from python_snaptime.models import Snaptime


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
