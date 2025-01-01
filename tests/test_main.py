import re
from datetime import date, datetime

import pendulum
import pytest

from python_snaptime import snap


class TestSnap:
    @pytest.fixture()
    def pendulum_dtm(self):
        return pendulum.datetime(2024, 12, 30, 13, 1, 10, 999999)

    @pytest.fixture()
    def datetime_dtm(self):
        return datetime(2024, 12, 30, 13, 1, 10, 999999)

    def test_snap_invalid_datetime(self):
        # arrage
        dtm = date(2024, 12, 30)

        # arrange/act
        with pytest.raises(
            TypeError, match=re.escape("Invalid datetime type. Must be pendulum.DateTime or datetime.datetime.")
        ):
            snap(dtm, "@d")

    @pytest.mark.parametrize(
        "snaptime,snap_dtm",
        [
            ("@d-1h", pendulum.datetime(2024, 12, 29, 23, 0, 0, 000000)),
        ],
    )
    def test_snap(self, snaptime: str, snap_dtm: pendulum.DateTime, pendulum_dtm: pendulum.DateTime):
        # act
        result = snap(pendulum_dtm, snaptime)

        # assert
        assert result == snap_dtm
