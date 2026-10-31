import re
import time
from dataclasses import FrozenInstanceError
from datetime import date, datetime, timedelta, timezone, tzinfo
from zoneinfo import ZoneInfo

import pendulum
import pytest
import python_snaptime
from python_snaptime import (
    NOW,
    Action,
    CompiledSnaptime,
    Snaptime,
    SnaptimeError,
    Unit,
    Weekday,
    apply,
    compile,
    parse,
    snap,
    snap_now,
    snap_range,
)


class TestSnap:
    @pytest.fixture()
    def pendulum_dtm(self):
        return pendulum.datetime(2024, 12, 30, 13, 1, 10, 999999)

    @pytest.fixture()
    def pendulum_dtm_timezone(self):
        return pendulum.datetime(2024, 12, 30, 13, 1, 10, 999999, tz=pendulum.timezone("America/New_York"))

    @pytest.fixture()
    def datetime_dtm(self):
        return datetime(2024, 12, 30, 13, 1, 10, 999999)

    @pytest.fixture()
    def datetime_dtm_timezone(self):
        return datetime(2024, 12, 30, 13, 1, 10, 999999, tzinfo=ZoneInfo("America/New_York"))

    def test_snap_invalid_datetime(self):
        # arrage
        dtm = "2024-12-30"

        # arrange/act
        with pytest.raises(
            TypeError,
            match=re.escape(
                "Invalid datetime type. Must be pendulum.DateTime, datetime.datetime, pendulum.Date or datetime.date."
            ),
        ):
            snap(dtm, "@d-2h")

    @pytest.mark.parametrize(
        "snaptime,snap_dtm",
        [
            ("@d", pendulum.datetime(2024, 12, 30, 0, 0, 0, 0)),
            ("@h-2h", pendulum.datetime(2024, 12, 30, 11, 0, 0, 0)),
            ("@m+30m", pendulum.datetime(2024, 12, 30, 13, 31, 0, 0)),
            ("@s-500ms", pendulum.datetime(2024, 12, 30, 13, 1, 9, 500000)),
            ("@w@d+1000us", pendulum.datetime(2024, 12, 30, 0, 0, 0, 1000)),
            ("@mon-1w+250ms", pendulum.datetime(2024, 11, 24, 0, 0, 0, 250000)),
            ("@q+1mon-750us", pendulum.datetime(2024, 10, 31, 23, 59, 59, 999250)),
            ("@y@q+1500ms", pendulum.datetime(2024, 1, 1, 0, 0, 1, 500000)),
            ("@d@h-6h+3s", pendulum.datetime(2024, 12, 29, 18, 0, 3, 0)),
            ("@h@m+45m-2s", pendulum.datetime(2024, 12, 30, 13, 44, 58, 0)),
            ("@w-2d@d+100ms", pendulum.datetime(2024, 12, 28, 0, 0, 0, 100000)),
            ("@mon+1w@w-250us", pendulum.datetime(2024, 12, 1, 23, 59, 59, 999750)),
            ("@q-1mon@mon+1s", pendulum.datetime(2024, 9, 1, 0, 0, 1, 0)),
            ("@y+3mon@q-750ms", pendulum.datetime(2024, 3, 31, 23, 59, 59, 250000)),
            ("@d@h@m-30m+500us", pendulum.datetime(2024, 12, 29, 23, 30, 0, 500)),
            ("@h-4h@m+15m-1s", pendulum.datetime(2024, 12, 30, 9, 14, 59, 0)),
            ("@w+3d@d-12h+350ms", pendulum.datetime(2025, 1, 1, 12, 0, 0, 350000)),
            ("@mon-2w@w+4d-1250us", pendulum.datetime(2024, 11, 14, 23, 59, 59, 998750)),
            ("@q+2mon@mon-1w+2s", pendulum.datetime(2024, 11, 24, 0, 0, 2, 0)),
            ("@y-1q@q+1mon-900ms", pendulum.datetime(2023, 10, 31, 23, 59, 59, 100000)),
            ("@d+1d@h-6h@m+1500us", pendulum.datetime(2024, 12, 30, 18, 0, 0, 1500)),
            ("@h@m-45m@s+30s", pendulum.datetime(2024, 12, 30, 12, 15, 30, 0)),
            ("@w@d-1d@h+12h-750ms", pendulum.datetime(2024, 12, 29, 11, 59, 59, 250000)),
            ("@mon@w+1w@d-3d+1s", pendulum.datetime(2024, 11, 29, 0, 0, 1, 0)),
            ("@q@mon-2mon@w+1w-500us", pendulum.datetime(2024, 8, 4, 23, 59, 59, 999500)),
            ("@y@q+1q@mon-2mon+3s", pendulum.datetime(2024, 2, 1, 0, 0, 3, 0)),
            ("@d@h-12h@m+30m@s-1750ms", pendulum.datetime(2024, 12, 29, 12, 29, 58, 250000)),
            ("@h-3h@m+45m@s-15s", pendulum.datetime(2024, 12, 30, 10, 44, 45, 0)),
            ("@w+2d@d-1d@h+6h+2000us", pendulum.datetime(2024, 12, 31, 6, 0, 0, 2000)),
            ("@mon-3w@w+1w@d-2d-1s", pendulum.datetime(2024, 11, 8, 23, 59, 59, 0)),
            ("@q+1mon@mon-2w@w+3d+850ms", pendulum.datetime(2024, 10, 17, 0, 0, 0, 850000)),
            ("@y-2q@q+2mon@mon-3w-1500us", pendulum.datetime(2023, 8, 10, 23, 59, 59, 998500)),
            ("@d+2d@h-18h@m+45m@s+4s", pendulum.datetime(2024, 12, 31, 6, 45, 4, 0)),
            ("@h@m-50m@s+45s@m+5m", pendulum.datetime(2024, 12, 30, 12, 15, 0, 0)),
            ("@w@d-3d@h+18h@m-30m+750ms", pendulum.datetime(2024, 12, 27, 17, 30, 0, 750000)),
            ("@mon@w+2w@d-4d@h+12h-2s", pendulum.datetime(2024, 12, 5, 11, 59, 58, 0)),
            ("@q@mon-1mon@w+2w@d-1d+1250us", pendulum.datetime(2024, 9, 8, 0, 0, 0, 1250)),
            ("@y@q+2q@mon-3mon@w+1w-3s", pendulum.datetime(2024, 4, 7, 23, 59, 57, 0)),
            ("@d@h@m@s-45s@m+15m+500ms", pendulum.datetime(2024, 12, 30, 0, 14, 0, 500000)),
            ("@h-5h@m+50m@s-40s@m+10m-750us", pendulum.datetime(2024, 12, 30, 8, 58, 59, 999250)),
            ("@w+3d@d-2d@h+14h@m-45m+1s", pendulum.datetime(2024, 12, 31, 13, 15, 1, 0)),
            ("@mon-2w@w+10d@d-5d@h+8h-1000ms", pendulum.datetime(2024, 11, 16, 7, 59, 59, 0)),
            ("@q+2mon@mon-6w@w+3w@d-2d+2s", pendulum.datetime(2024, 11, 2, 0, 0, 2, 0)),
            ("@y-1y@q+2q@mon-4mon@w+2w-1500us", pendulum.datetime(2023, 3, 12, 23, 59, 59, 998500)),
            ("@d+3d@h-36h@m+90m@s-120s+250ms", pendulum.datetime(2024, 12, 31, 13, 28, 0, 250000)),
            ("@h@m@s-55s@m+25m@h-1h@m+35m-500us", pendulum.datetime(2024, 12, 30, 12, 34, 59, 999500)),
            ("@w@d@h-30h@m+150m@s-300s@m+60m+2000ms", pendulum.datetime(2024, 12, 28, 21, 25, 2, 0)),
            ("@mon@w@d-10d@h+120h@m-360m@s+1800s-750us", pendulum.datetime(2024, 11, 19, 18, 29, 59, 999250)),
            ("@q@mon@w-3w@d+15d@h-180h@m+600m+4s", pendulum.datetime(2024, 9, 16, 22, 0, 4, 0)),
            (
                "@y-2y@q+3q@mon-9mon@w+26w@d-150d@h+1800h@m-54000m@s+3240000s-1500ms+2000us",
                pendulum.datetime(2022, 4, 12, 23, 59, 58, 502000),
            ),
        ],
    )
    def test_snap_pendulum(self, snaptime: str, snap_dtm: pendulum.DateTime, pendulum_dtm: pendulum.DateTime):
        # act
        result = snap(pendulum_dtm, snaptime)

        # assert
        assert result == snap_dtm

    @pytest.mark.parametrize(
        "snaptime,snap_dtm",
        [
            ("@d", pendulum.datetime(2024, 12, 30, 0, 0, 0, 0, tz=pendulum.timezone("America/New_York"))),
            ("@h-2h", pendulum.datetime(2024, 12, 30, 11, 0, 0, 0, tz=pendulum.timezone("America/New_York"))),
            ("@m+30m", pendulum.datetime(2024, 12, 30, 13, 31, 0, 0, tz=pendulum.timezone("America/New_York"))),
            ("@s-500ms", pendulum.datetime(2024, 12, 30, 13, 1, 9, 500000, tz=pendulum.timezone("America/New_York"))),
            ("@w@d+1000us", pendulum.datetime(2024, 12, 30, 0, 0, 0, 1000, tz=pendulum.timezone("America/New_York"))),
            (
                "@mon-1w+250ms",
                pendulum.datetime(2024, 11, 24, 0, 0, 0, 250000, tz=pendulum.timezone("America/New_York")),
            ),
            (
                "@q+1mon-750us",
                pendulum.datetime(2024, 10, 31, 23, 59, 59, 999250, tz=pendulum.timezone("America/New_York")),
            ),
            ("@y@q+1500ms", pendulum.datetime(2024, 1, 1, 0, 0, 1, 500000, tz=pendulum.timezone("America/New_York"))),
            ("@d@h-6h+3s", pendulum.datetime(2024, 12, 29, 18, 0, 3, 0, tz=pendulum.timezone("America/New_York"))),
            ("@h@m+45m-2s", pendulum.datetime(2024, 12, 30, 13, 44, 58, 0, tz=pendulum.timezone("America/New_York"))),
            (
                "@w-2d@d+100ms",
                pendulum.datetime(2024, 12, 28, 0, 0, 0, 100000, tz=pendulum.timezone("America/New_York")),
            ),
            (
                "@mon+1w@w-250us",
                pendulum.datetime(2024, 12, 1, 23, 59, 59, 999750, tz=pendulum.timezone("America/New_York")),
            ),
            ("@q-1mon@mon+1s", pendulum.datetime(2024, 9, 1, 0, 0, 1, 0, tz=pendulum.timezone("America/New_York"))),
            (
                "@y+3mon@q-750ms",
                pendulum.datetime(2024, 3, 31, 23, 59, 59, 250000, tz=pendulum.timezone("America/New_York")),
            ),
            (
                "@d@h@m-30m+500us",
                pendulum.datetime(2024, 12, 29, 23, 30, 0, 500, tz=pendulum.timezone("America/New_York")),
            ),
            ("@h-4h@m+15m-1s", pendulum.datetime(2024, 12, 30, 9, 14, 59, 0, tz=pendulum.timezone("America/New_York"))),
            (
                "@w+3d@d-12h+350ms",
                pendulum.datetime(2025, 1, 1, 12, 0, 0, 350000, tz=pendulum.timezone("America/New_York")),
            ),
            (
                "@mon-2w@w+4d-1250us",
                pendulum.datetime(2024, 11, 14, 23, 59, 59, 998750, tz=pendulum.timezone("America/New_York")),
            ),
            (
                "@q+2mon@mon-1w+2s",
                pendulum.datetime(2024, 11, 24, 0, 0, 2, 0, tz=pendulum.timezone("America/New_York")),
            ),
            (
                "@y-1q@q+1mon-900ms",
                pendulum.datetime(2023, 10, 31, 23, 59, 59, 100000, tz=pendulum.timezone("America/New_York")),
            ),
            (
                "@d+1d@h-6h@m+1500us",
                pendulum.datetime(2024, 12, 30, 18, 0, 0, 1500, tz=pendulum.timezone("America/New_York")),
            ),
            (
                "@h@m-45m@s+30s",
                pendulum.datetime(2024, 12, 30, 12, 15, 30, 0, tz=pendulum.timezone("America/New_York")),
            ),
            (
                "@w@d-1d@h+12h-750ms",
                pendulum.datetime(2024, 12, 29, 11, 59, 59, 250000, tz=pendulum.timezone("America/New_York")),
            ),
            (
                "@mon@w+1w@d-3d+1s",
                pendulum.datetime(2024, 11, 29, 0, 0, 1, 0, tz=pendulum.timezone("America/New_York")),
            ),
            (
                "@q@mon-2mon@w+1w-500us",
                pendulum.datetime(2024, 8, 4, 23, 59, 59, 999500, tz=pendulum.timezone("America/New_York")),
            ),
            (
                "@y@q+1q@mon-2mon+3s",
                pendulum.datetime(2024, 2, 1, 0, 0, 3, 0, tz=pendulum.timezone("America/New_York")),
            ),
            (
                "@d@h-12h@m+30m@s-1750ms",
                pendulum.datetime(2024, 12, 29, 12, 29, 58, 250000, tz=pendulum.timezone("America/New_York")),
            ),
            (
                "@h-3h@m+45m@s-15s",
                pendulum.datetime(2024, 12, 30, 10, 44, 45, 0, tz=pendulum.timezone("America/New_York")),
            ),
            (
                "@w+2d@d-1d@h+6h+2000us",
                pendulum.datetime(2024, 12, 31, 6, 0, 0, 2000, tz=pendulum.timezone("America/New_York")),
            ),
            (
                "@mon-3w@w+1w@d-2d-1s",
                pendulum.datetime(2024, 11, 8, 23, 59, 59, 0, tz=pendulum.timezone("America/New_York")),
            ),
            (
                "@q+1mon@mon-2w@w+3d+850ms",
                pendulum.datetime(2024, 10, 17, 0, 0, 0, 850000, tz=pendulum.timezone("America/New_York")),
            ),
            (
                "@y-2q@q+2mon@mon-3w-1500us",
                pendulum.datetime(2023, 8, 10, 23, 59, 59, 998500, tz=pendulum.timezone("America/New_York")),
            ),
            (
                "@d+2d@h-18h@m+45m@s+4s",
                pendulum.datetime(2024, 12, 31, 6, 45, 4, 0, tz=pendulum.timezone("America/New_York")),
            ),
            (
                "@h@m-50m@s+45s@m+5m",
                pendulum.datetime(2024, 12, 30, 12, 15, 0, 0, tz=pendulum.timezone("America/New_York")),
            ),
            (
                "@w@d-3d@h+18h@m-30m+750ms",
                pendulum.datetime(2024, 12, 27, 17, 30, 0, 750000, tz=pendulum.timezone("America/New_York")),
            ),
            (
                "@mon@w+2w@d-4d@h+12h-2s",
                pendulum.datetime(2024, 12, 5, 11, 59, 58, 0, tz=pendulum.timezone("America/New_York")),
            ),
            (
                "@q@mon-1mon@w+2w@d-1d+1250us",
                pendulum.datetime(2024, 9, 8, 0, 0, 0, 1250, tz=pendulum.timezone("America/New_York")),
            ),
            (
                "@y@q+2q@mon-3mon@w+1w-3s",
                pendulum.datetime(2024, 4, 7, 23, 59, 57, 0, tz=pendulum.timezone("America/New_York")),
            ),
            (
                "@d@h@m@s-45s@m+15m+500ms",
                pendulum.datetime(2024, 12, 30, 0, 14, 0, 500000, tz=pendulum.timezone("America/New_York")),
            ),
            (
                "@h-5h@m+50m@s-40s@m+10m-750us",
                pendulum.datetime(2024, 12, 30, 8, 58, 59, 999250, tz=pendulum.timezone("America/New_York")),
            ),
            (
                "@w+3d@d-2d@h+14h@m-45m+1s",
                pendulum.datetime(2024, 12, 31, 13, 15, 1, 0, tz=pendulum.timezone("America/New_York")),
            ),
            (
                "@mon-2w@w+10d@d-5d@h+8h-1000ms",
                pendulum.datetime(2024, 11, 16, 7, 59, 59, 0, tz=pendulum.timezone("America/New_York")),
            ),
            (
                "@q+2mon@mon-6w@w+3w@d-2d+2s",
                pendulum.datetime(2024, 11, 2, 0, 0, 2, 0, tz=pendulum.timezone("America/New_York")),
            ),
            (
                "@y-1y@q+2q@mon-4mon@w+2w-1500us",
                pendulum.datetime(2023, 3, 12, 23, 59, 59, 998500, tz=pendulum.timezone("America/New_York")),
            ),
            (
                "@d+3d@h-36h@m+90m@s-120s+250ms",
                pendulum.datetime(2024, 12, 31, 13, 28, 0, 250000, tz=pendulum.timezone("America/New_York")),
            ),
            (
                "@h@m@s-55s@m+25m@h-1h@m+35m-500us",
                pendulum.datetime(2024, 12, 30, 12, 34, 59, 999500, tz=pendulum.timezone("America/New_York")),
            ),
            (
                "@w@d@h-30h@m+150m@s-300s@m+60m+2000ms",
                pendulum.datetime(2024, 12, 28, 21, 25, 2, 0, tz=pendulum.timezone("America/New_York")),
            ),
            (
                "@mon@w@d-10d@h+120h@m-360m@s+1800s-750us",
                pendulum.datetime(2024, 11, 19, 18, 29, 59, 999250, tz=pendulum.timezone("America/New_York")),
            ),
            (
                "@q@mon@w-3w@d+15d@h-180h@m+600m+4s",
                pendulum.datetime(2024, 9, 16, 22, 0, 4, 0, tz=pendulum.timezone("America/New_York")),
            ),
            (
                "@y-2y@q+3q@mon-9mon@w+26w@d-150d@h+1800h@m-54000m@s+3240000s-1500ms+2000us",
                pendulum.datetime(2022, 4, 13, 0, 59, 58, 502000, tz=pendulum.timezone("America/New_York")),
            ),
        ],
    )
    def test_snap_pendulum_timezone(
        self, snaptime: str, snap_dtm: pendulum.DateTime, pendulum_dtm_timezone: pendulum.DateTime
    ):
        # act
        result = snap(pendulum_dtm_timezone, snaptime)

        # assert
        assert result == snap_dtm

    @pytest.mark.parametrize(
        "snaptime,snap_dtm",
        [
            ("@d", datetime(2024, 12, 30, 0, 0, 0, 0)),
            ("@h-2h", datetime(2024, 12, 30, 11, 0, 0, 0)),
            ("@m+30m", datetime(2024, 12, 30, 13, 31, 0, 0)),
            ("@s-500ms", datetime(2024, 12, 30, 13, 1, 9, 500000)),
            ("@w@d+1000us", datetime(2024, 12, 30, 0, 0, 0, 1000)),
            ("@mon-1w+250ms", datetime(2024, 11, 24, 0, 0, 0, 250000)),
            ("@q+1mon-750us", datetime(2024, 10, 31, 23, 59, 59, 999250)),
            ("@y@q+1500ms", datetime(2024, 1, 1, 0, 0, 1, 500000)),
            ("@d@h-6h+3s", datetime(2024, 12, 29, 18, 0, 3, 0)),
            ("@h@m+45m-2s", datetime(2024, 12, 30, 13, 44, 58, 0)),
            ("@w-2d@d+100ms", datetime(2024, 12, 28, 0, 0, 0, 100000)),
            ("@mon+1w@w-250us", datetime(2024, 12, 1, 23, 59, 59, 999750)),
            ("@q-1mon@mon+1s", datetime(2024, 9, 1, 0, 0, 1, 0)),
            ("@y+3mon@q-750ms", datetime(2024, 3, 31, 23, 59, 59, 250000)),
            ("@d@h@m-30m+500us", datetime(2024, 12, 29, 23, 30, 0, 500)),
            ("@h-4h@m+15m-1s", datetime(2024, 12, 30, 9, 14, 59, 0)),
            ("@w+3d@d-12h+350ms", datetime(2025, 1, 1, 12, 0, 0, 350000)),
            ("@mon-2w@w+4d-1250us", datetime(2024, 11, 14, 23, 59, 59, 998750)),
            ("@q+2mon@mon-1w+2s", datetime(2024, 11, 24, 0, 0, 2, 0)),
            ("@y-1q@q+1mon-900ms", datetime(2023, 10, 31, 23, 59, 59, 100000)),
            ("@d+1d@h-6h@m+1500us", datetime(2024, 12, 30, 18, 0, 0, 1500)),
            ("@h@m-45m@s+30s", datetime(2024, 12, 30, 12, 15, 30, 0)),
            ("@w@d-1d@h+12h-750ms", datetime(2024, 12, 29, 11, 59, 59, 250000)),
            ("@mon@w+1w@d-3d+1s", datetime(2024, 11, 29, 0, 0, 1, 0)),
            ("@q@mon-2mon@w+1w-500us", datetime(2024, 8, 4, 23, 59, 59, 999500)),
            ("@y@q+1q@mon-2mon+3s", datetime(2024, 2, 1, 0, 0, 3, 0)),
            ("@d@h-12h@m+30m@s-1750ms", datetime(2024, 12, 29, 12, 29, 58, 250000)),
            ("@h-3h@m+45m@s-15s", datetime(2024, 12, 30, 10, 44, 45, 0)),
            ("@w+2d@d-1d@h+6h+2000us", datetime(2024, 12, 31, 6, 0, 0, 2000)),
            ("@mon-3w@w+1w@d-2d-1s", datetime(2024, 11, 8, 23, 59, 59, 0)),
            ("@q+1mon@mon-2w@w+3d+850ms", datetime(2024, 10, 17, 0, 0, 0, 850000)),
            ("@y-2q@q+2mon@mon-3w-1500us", datetime(2023, 8, 10, 23, 59, 59, 998500)),
            ("@d+2d@h-18h@m+45m@s+4s", datetime(2024, 12, 31, 6, 45, 4, 0)),
            ("@h@m-50m@s+45s@m+5m", datetime(2024, 12, 30, 12, 15, 0, 0)),
            ("@w@d-3d@h+18h@m-30m+750ms", datetime(2024, 12, 27, 17, 30, 0, 750000)),
            ("@mon@w+2w@d-4d@h+12h-2s", datetime(2024, 12, 5, 11, 59, 58, 0)),
            ("@q@mon-1mon@w+2w@d-1d+1250us", datetime(2024, 9, 8, 0, 0, 0, 1250)),
            ("@y@q+2q@mon-3mon@w+1w-3s", datetime(2024, 4, 7, 23, 59, 57, 0)),
            ("@d@h@m@s-45s@m+15m+500ms", datetime(2024, 12, 30, 0, 14, 0, 500000)),
            ("@h-5h@m+50m@s-40s@m+10m-750us", datetime(2024, 12, 30, 8, 58, 59, 999250)),
            ("@w+3d@d-2d@h+14h@m-45m+1s", datetime(2024, 12, 31, 13, 15, 1, 0)),
            ("@mon-2w@w+10d@d-5d@h+8h-1000ms", datetime(2024, 11, 16, 7, 59, 59, 0)),
            ("@q+2mon@mon-6w@w+3w@d-2d+2s", datetime(2024, 11, 2, 0, 0, 2, 0)),
            ("@y-1y@q+2q@mon-4mon@w+2w-1500us", datetime(2023, 3, 12, 23, 59, 59, 998500)),
            ("@d+3d@h-36h@m+90m@s-120s+250ms", datetime(2024, 12, 31, 13, 28, 0, 250000)),
            ("@h@m@s-55s@m+25m@h-1h@m+35m-500us", datetime(2024, 12, 30, 12, 34, 59, 999500)),
            ("@w@d@h-30h@m+150m@s-300s@m+60m+2000ms", datetime(2024, 12, 28, 21, 25, 2, 0)),
            ("@mon@w@d-10d@h+120h@m-360m@s+1800s-750us", datetime(2024, 11, 19, 18, 29, 59, 999250)),
            ("@q@mon@w-3w@d+15d@h-180h@m+600m+4s", datetime(2024, 9, 16, 22, 0, 4, 0)),
            (
                "@y-2y@q+3q@mon-9mon@w+26w@d-150d@h+1800h@m-54000m@s+3240000s-1500ms+2000us",
                datetime(2022, 4, 12, 23, 59, 58, 502000),
            ),
        ],
    )
    def test_snap_datetime(self, snaptime: str, snap_dtm: datetime, datetime_dtm: datetime):
        # act
        result = snap(datetime_dtm, snaptime)

        # assert
        assert result == snap_dtm

    @pytest.mark.parametrize(
        "snaptime,snap_dtm",
        [
            ("@d", datetime(2024, 12, 30, 0, 0, 0, 0, tzinfo=ZoneInfo("America/New_York"))),
            ("@h-2h", datetime(2024, 12, 30, 11, 0, 0, 0, tzinfo=ZoneInfo("America/New_York"))),
            ("@m+30m", datetime(2024, 12, 30, 13, 31, 0, 0, tzinfo=ZoneInfo("America/New_York"))),
            ("@s-500ms", datetime(2024, 12, 30, 13, 1, 9, 500000, tzinfo=ZoneInfo("America/New_York"))),
            ("@w@d+1000us", datetime(2024, 12, 30, 0, 0, 0, 1000, tzinfo=ZoneInfo("America/New_York"))),
            ("@mon-1w+250ms", datetime(2024, 11, 24, 0, 0, 0, 250000, tzinfo=ZoneInfo("America/New_York"))),
            ("@q+1mon-750us", datetime(2024, 10, 31, 23, 59, 59, 999250, tzinfo=ZoneInfo("America/New_York"))),
            ("@y@q+1500ms", datetime(2024, 1, 1, 0, 0, 1, 500000, tzinfo=ZoneInfo("America/New_York"))),
            ("@d@h-6h+3s", datetime(2024, 12, 29, 18, 0, 3, 0, tzinfo=ZoneInfo("America/New_York"))),
            ("@h@m+45m-2s", datetime(2024, 12, 30, 13, 44, 58, 0, tzinfo=ZoneInfo("America/New_York"))),
            ("@w-2d@d+100ms", datetime(2024, 12, 28, 0, 0, 0, 100000, tzinfo=ZoneInfo("America/New_York"))),
            ("@mon+1w@w-250us", datetime(2024, 12, 1, 23, 59, 59, 999750, tzinfo=ZoneInfo("America/New_York"))),
            ("@q-1mon@mon+1s", datetime(2024, 9, 1, 0, 0, 1, 0, tzinfo=ZoneInfo("America/New_York"))),
            ("@y+3mon@q-750ms", datetime(2024, 3, 31, 23, 59, 59, 250000, tzinfo=ZoneInfo("America/New_York"))),
            ("@d@h@m-30m+500us", datetime(2024, 12, 29, 23, 30, 0, 500, tzinfo=ZoneInfo("America/New_York"))),
            ("@h-4h@m+15m-1s", datetime(2024, 12, 30, 9, 14, 59, 0, tzinfo=ZoneInfo("America/New_York"))),
            ("@w+3d@d-12h+350ms", datetime(2025, 1, 1, 12, 0, 0, 350000, tzinfo=ZoneInfo("America/New_York"))),
            ("@mon-2w@w+4d-1250us", datetime(2024, 11, 14, 23, 59, 59, 998750, tzinfo=ZoneInfo("America/New_York"))),
            ("@q+2mon@mon-1w+2s", datetime(2024, 11, 24, 0, 0, 2, 0, tzinfo=ZoneInfo("America/New_York"))),
            ("@y-1q@q+1mon-900ms", datetime(2023, 10, 31, 23, 59, 59, 100000, tzinfo=ZoneInfo("America/New_York"))),
            ("@d+1d@h-6h@m+1500us", datetime(2024, 12, 30, 18, 0, 0, 1500, tzinfo=ZoneInfo("America/New_York"))),
            ("@h@m-45m@s+30s", datetime(2024, 12, 30, 12, 15, 30, 0, tzinfo=ZoneInfo("America/New_York"))),
            ("@w@d-1d@h+12h-750ms", datetime(2024, 12, 29, 11, 59, 59, 250000, tzinfo=ZoneInfo("America/New_York"))),
            ("@mon@w+1w@d-3d+1s", datetime(2024, 11, 29, 0, 0, 1, 0, tzinfo=ZoneInfo("America/New_York"))),
            ("@q@mon-2mon@w+1w-500us", datetime(2024, 8, 4, 23, 59, 59, 999500, tzinfo=ZoneInfo("America/New_York"))),
            ("@y@q+1q@mon-2mon+3s", datetime(2024, 2, 1, 0, 0, 3, 0, tzinfo=ZoneInfo("America/New_York"))),
            (
                "@d@h-12h@m+30m@s-1750ms",
                datetime(2024, 12, 29, 12, 29, 58, 250000, tzinfo=ZoneInfo("America/New_York")),
            ),
            ("@h-3h@m+45m@s-15s", datetime(2024, 12, 30, 10, 44, 45, 0, tzinfo=ZoneInfo("America/New_York"))),
            ("@w+2d@d-1d@h+6h+2000us", datetime(2024, 12, 31, 6, 0, 0, 2000, tzinfo=ZoneInfo("America/New_York"))),
            ("@mon-3w@w+1w@d-2d-1s", datetime(2024, 11, 8, 23, 59, 59, 0, tzinfo=ZoneInfo("America/New_York"))),
            ("@q+1mon@mon-2w@w+3d+850ms", datetime(2024, 10, 17, 0, 0, 0, 850000, tzinfo=ZoneInfo("America/New_York"))),
            (
                "@y-2q@q+2mon@mon-3w-1500us",
                datetime(2023, 8, 10, 23, 59, 59, 998500, tzinfo=ZoneInfo("America/New_York")),
            ),
            ("@d+2d@h-18h@m+45m@s+4s", datetime(2024, 12, 31, 6, 45, 4, 0, tzinfo=ZoneInfo("America/New_York"))),
            ("@h@m-50m@s+45s@m+5m", datetime(2024, 12, 30, 12, 15, 0, 0, tzinfo=ZoneInfo("America/New_York"))),
            (
                "@w@d-3d@h+18h@m-30m+750ms",
                datetime(2024, 12, 27, 17, 30, 0, 750000, tzinfo=ZoneInfo("America/New_York")),
            ),
            ("@mon@w+2w@d-4d@h+12h-2s", datetime(2024, 12, 5, 11, 59, 58, 0, tzinfo=ZoneInfo("America/New_York"))),
            ("@q@mon-1mon@w+2w@d-1d+1250us", datetime(2024, 9, 8, 0, 0, 0, 1250, tzinfo=ZoneInfo("America/New_York"))),
            ("@y@q+2q@mon-3mon@w+1w-3s", datetime(2024, 4, 7, 23, 59, 57, 0, tzinfo=ZoneInfo("America/New_York"))),
            ("@d@h@m@s-45s@m+15m+500ms", datetime(2024, 12, 30, 0, 14, 0, 500000, tzinfo=ZoneInfo("America/New_York"))),
            (
                "@h-5h@m+50m@s-40s@m+10m-750us",
                datetime(2024, 12, 30, 8, 58, 59, 999250, tzinfo=ZoneInfo("America/New_York")),
            ),
            ("@w+3d@d-2d@h+14h@m-45m+1s", datetime(2024, 12, 31, 13, 15, 1, 0, tzinfo=ZoneInfo("America/New_York"))),
            (
                "@mon-2w@w+10d@d-5d@h+8h-1000ms",
                datetime(2024, 11, 16, 7, 59, 59, 0, tzinfo=ZoneInfo("America/New_York")),
            ),
            ("@q+2mon@mon-6w@w+3w@d-2d+2s", datetime(2024, 11, 2, 0, 0, 2, 0, tzinfo=ZoneInfo("America/New_York"))),
            (
                "@y-1y@q+2q@mon-4mon@w+2w-1500us",
                datetime(2023, 3, 12, 23, 59, 59, 998500, tzinfo=ZoneInfo("America/New_York")),
            ),
            (
                "@d+3d@h-36h@m+90m@s-120s+250ms",
                datetime(2024, 12, 31, 13, 28, 0, 250000, tzinfo=ZoneInfo("America/New_York")),
            ),
            (
                "@h@m@s-55s@m+25m@h-1h@m+35m-500us",
                datetime(2024, 12, 30, 12, 34, 59, 999500, tzinfo=ZoneInfo("America/New_York")),
            ),
            (
                "@w@d@h-30h@m+150m@s-300s@m+60m+2000ms",
                datetime(2024, 12, 28, 21, 25, 2, 0, tzinfo=ZoneInfo("America/New_York")),
            ),
            (
                "@mon@w@d-10d@h+120h@m-360m@s+1800s-750us",
                datetime(2024, 11, 19, 18, 29, 59, 999250, tzinfo=ZoneInfo("America/New_York")),
            ),
            (
                "@q@mon@w-3w@d+15d@h-180h@m+600m+4s",
                datetime(2024, 9, 16, 22, 0, 4, 0, tzinfo=ZoneInfo("America/New_York")),
            ),
            (
                "@y-2y@q+3q@mon-9mon@w+26w@d-150d@h+1800h@m-54000m@s+3240000s-1500ms+2000us",
                datetime(2022, 4, 13, 0, 59, 58, 502000, tzinfo=ZoneInfo("America/New_York")),
            ),
        ],
    )
    def test_snap_datetime_timzeone(self, snaptime: str, snap_dtm: datetime, datetime_dtm_timezone: datetime):
        # act
        result = snap(datetime_dtm_timezone, snaptime)

        # assert
        assert result == snap_dtm

    @pytest.mark.parametrize(
        "tz",
        [ZoneInfo("America/New_York"), timezone.utc, timezone(timedelta(hours=5, minutes=30))],
    )
    def test_snap_datetime_keeps_tzinfo(self, tz: tzinfo):
        # arrange
        dtm = datetime(2024, 12, 30, 13, 1, 10, 999999, tzinfo=tz)

        # act
        result = snap(dtm, "@d-2h")

        # assert
        assert result.tzinfo is tz
        assert result == datetime(2024, 12, 29, 22, 0, 0, 0, tzinfo=tz)

    def test_snap_datetime_zoneinfo_across_dst(self):
        # arrange
        dtm = datetime(2024, 11, 3, 12, 0, 0, tzinfo=ZoneInfo("America/New_York"))

        # act
        result = snap(dtm, "@d")

        # assert
        assert result == datetime(2024, 11, 3, 0, 0, 0, tzinfo=ZoneInfo("America/New_York"))
        assert result.utcoffset() == timedelta(hours=-4)

    @pytest.fixture()
    def local_tz_with_dst(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("TZ", "Europe/London")
        time.tzset()
        yield
        monkeypatch.undo()
        time.tzset()

    @pytest.mark.usefixtures("local_tz_with_dst")
    def test_snap_datetime_naive_ignores_local_dst(self):
        # arrange
        dtm = datetime(2024, 3, 31, 1, 30, 0, 123457)

        # act
        result = snap(dtm, "@h")

        # assert
        assert type(result) is datetime
        assert result == datetime(2024, 3, 31, 1, 0, 0)

    @pytest.mark.parametrize(
        "week_start,snap_dtm",
        [
            (Weekday.MONDAY, pendulum.datetime(2024, 12, 30)),
            (Weekday.SUNDAY, pendulum.datetime(2024, 12, 29)),
            (Weekday.SATURDAY, pendulum.datetime(2024, 12, 28)),
            (Weekday.TUESDAY, pendulum.datetime(2024, 12, 31)),
        ],
    )
    def test_snap_week_start_pendulum(self, week_start: Weekday, snap_dtm: pendulum.DateTime):
        # arrange
        dtm = pendulum.datetime(2024, 12, 31)

        # act
        result = snap(dtm, "@w", week_start=week_start)

        # assert
        assert type(result) is pendulum.DateTime
        assert result == snap_dtm

    def test_snap_week_start_default_is_monday(self):
        # act
        result = snap(pendulum.datetime(2024, 12, 31), "@w")

        # assert
        assert type(result) is pendulum.DateTime
        assert result == pendulum.datetime(2024, 12, 30)

    def test_snap_week_start_datetime(self, datetime_dtm: datetime):
        # act
        result = snap(datetime_dtm, "@w-1d", week_start=Weekday.SUNDAY)

        # assert
        assert type(result) is datetime
        assert result == datetime(2024, 12, 28, 0, 0, 0)

    def test_snap_week_start_datetime_timezone(self, datetime_dtm_timezone: datetime):
        # act
        result = snap(datetime_dtm_timezone, "@w", week_start=Weekday.WEDNESDAY)

        # assert
        assert type(result) is datetime
        assert result == datetime(2024, 12, 25, 0, 0, 0, tzinfo=ZoneInfo("America/New_York"))
        assert result.tzinfo == ZoneInfo("America/New_York")

    def test_snap_week_start_pendulum_timezone(self, pendulum_dtm_timezone: pendulum.DateTime):
        # act
        result = snap(pendulum_dtm_timezone, "@w", week_start=Weekday.WEDNESDAY)

        # assert
        assert type(result) is pendulum.DateTime
        assert result == pendulum.datetime(2024, 12, 25, tz=pendulum.timezone("America/New_York"))
        assert result.timezone_name == "America/New_York"

    @pytest.mark.parametrize(
        "snaptime,day",
        [
            ("@w0", 29),
            ("@w1", 30),
            ("@w2", 24),
            ("@w3", 25),
            ("@w4", 26),
            ("@w5", 27),
            ("@w6", 28),
            ("@w7", 29),
        ],
    )
    def test_snap_weekday(self, snaptime: str, day: int):
        # arrange
        dtm = pendulum.datetime(2024, 12, 30, 18, 52)

        # act
        result = snap(dtm, snaptime)

        # assert
        assert type(result) is pendulum.DateTime
        assert result == pendulum.datetime(2024, 12, day)

    @pytest.mark.parametrize(
        "snaptime,weekday_name",
        [
            ("@w0", "Sunday"),
            ("@w1", "Monday"),
            ("@w2", "Tuesday"),
            ("@w3", "Wednesday"),
            ("@w4", "Thursday"),
            ("@w5", "Friday"),
            ("@w6", "Saturday"),
            ("@w7", "Sunday"),
        ],
    )
    def test_snap_weekday_datetime(self, datetime_dtm: datetime, snaptime: str, weekday_name: str):
        # act
        result = snap(datetime_dtm, snaptime)

        # assert
        assert type(result) is datetime
        assert result.strftime("%A") == weekday_name
        assert result.time() == datetime.min.time()
        assert timedelta(0) <= datetime_dtm - result < timedelta(days=7)

    @pytest.mark.parametrize(
        "dtm",
        [
            pendulum.datetime(2024, 12, 27, 0, 0, 0),
            pendulum.datetime(2024, 12, 27, 13, 1, 10, 999999),
            pendulum.datetime(2024, 12, 27, 23, 59, 59, 999999),
        ],
    )
    def test_snap_weekday_same_day(self, dtm: pendulum.DateTime):
        # act
        result = snap(dtm, "@w5")

        # assert
        assert type(result) is pendulum.DateTime
        assert result == pendulum.datetime(2024, 12, 27)

    def test_snap_weekday_day_after(self):
        # act
        result = snap(pendulum.datetime(2024, 12, 27, 23, 59), "@w6")

        # assert
        assert result == pendulum.datetime(2024, 12, 21)

    @pytest.mark.parametrize(
        "snaptime,snap_dtm",
        [
            ("-7d@w1", datetime(2024, 12, 23)),
            ("@w1-7d", datetime(2024, 12, 23)),
            ("@w5+1d@w1", datetime(2024, 12, 23)),
            ("@w0+12h", datetime(2024, 12, 29, 12)),
            ("@mon@w3", datetime(2024, 11, 27)),
        ],
    )
    def test_snap_weekday_chain(self, datetime_dtm: datetime, snaptime: str, snap_dtm: datetime):
        # act
        result = snap(datetime_dtm, snaptime)

        # assert
        assert type(result) is datetime
        assert result == snap_dtm

    @pytest.mark.parametrize("week_start", list(Weekday))
    def test_snap_weekday_ignores_week_start(self, pendulum_dtm: pendulum.DateTime, week_start: Weekday):
        # act
        result = snap(pendulum_dtm, "@w5", week_start=week_start)

        # assert
        assert type(result) is pendulum.DateTime
        assert result == pendulum.datetime(2024, 12, 27)

    def test_snap_weekday_pendulum_timezone(self, pendulum_dtm_timezone: pendulum.DateTime):
        # act
        result = snap(pendulum_dtm_timezone, "@w0")

        # assert
        assert type(result) is pendulum.DateTime
        assert result == pendulum.datetime(2024, 12, 29, tz=pendulum.timezone("America/New_York"))
        assert result.timezone_name == "America/New_York"

    def test_snap_weekday_datetime_timezone(self, datetime_dtm_timezone: datetime):
        # act
        result = snap(datetime_dtm_timezone, "@w0")

        # assert
        assert type(result) is datetime
        assert result == datetime(2024, 12, 29, tzinfo=ZoneInfo("America/New_York"))
        assert result.tzinfo == ZoneInfo("America/New_York")

    @pytest.mark.parametrize(
        "dtm,expected_type",
        [
            (pendulum.datetime(2024, 12, 30, 13, 1, 10), pendulum.DateTime),
            (pendulum.datetime(2024, 12, 30, 13, 1, 10, tz="America/New_York"), pendulum.DateTime),
            (datetime(2024, 12, 30, 13, 1, 10), datetime),
            (datetime(2024, 12, 30, 13, 1, 10, tzinfo=ZoneInfo("America/New_York")), datetime),
            (datetime(2024, 12, 30, 13, 1, 10, tzinfo=timezone.utc), datetime),
        ],
    )
    def test_snap_returns_input_type(self, dtm: datetime, expected_type: type[datetime]):
        # act
        result = snap(dtm, "@d-2h+10m")

        # assert
        assert type(result) is expected_type

    @pytest.mark.parametrize("snaptime", ["now", NOW])
    @pytest.mark.parametrize(
        "dtm,expected_type",
        [
            (pendulum.datetime(2024, 12, 30, 18, 52, 30, 123456), pendulum.DateTime),
            (pendulum.datetime(2024, 12, 30, 18, 52, 30, 123456, tz="America/New_York"), pendulum.DateTime),
            (datetime(2024, 12, 30, 18, 52, 30, 123456), datetime),
            (datetime(2024, 12, 30, 18, 52, 30, 123456, tzinfo=ZoneInfo("America/New_York")), datetime),
        ],
        ids=["pendulum", "pendulum_timezone", "datetime_naive", "datetime_aware"],
    )
    def test_snap_now_keyword(self, dtm: datetime, expected_type: type[datetime], snaptime: str):
        # act
        result = snap(dtm, snaptime)

        # assert
        assert result == dtm
        assert type(result) is expected_type
        assert result.tzinfo is dtm.tzinfo

    @pytest.mark.parametrize("snaptime", ["now-1d", "@dnow", "NOW", "now()"])
    def test_snap_now_keyword_invalid(self, snaptime: str):
        # act/assert
        with pytest.raises(SnaptimeError, match="Snaptime string is invalid"):
            snap(pendulum.datetime(2024, 12, 30, 18, 52), snaptime)


class TestSnapMultiple:
    @pytest.fixture()
    def dtm(self):
        return pendulum.datetime(2024, 12, 30, 18, 52, 37, 123456)

    @pytest.mark.parametrize(
        "snaptime,snap_dtm",
        [
            ("@15m", pendulum.datetime(2024, 12, 30, 18, 45)),
            ("@30m", pendulum.datetime(2024, 12, 30, 18, 30)),
            ("@10s", pendulum.datetime(2024, 12, 30, 18, 52, 30)),
            ("@4h", pendulum.datetime(2024, 12, 30, 16, 0)),
            ("@1m", pendulum.datetime(2024, 12, 30, 18, 52)),
            ("@d+7h@6h", pendulum.datetime(2024, 12, 30, 6, 0)),
            ("@15m-1h", pendulum.datetime(2024, 12, 30, 17, 45)),
        ],
    )
    def test_snap_multiple(self, dtm: pendulum.DateTime, snaptime: str, snap_dtm: pendulum.DateTime):
        # act
        result = snap(dtm, snaptime)

        # assert
        assert type(result) is pendulum.DateTime
        assert result == snap_dtm

    def test_snap_multiple_one_is_snap(self, dtm: pendulum.DateTime):
        # act/assert
        assert snap(dtm, "@1m") == snap(dtm, "@m")
        assert snap(dtm, "@1s") == snap(dtm, "@s")
        assert snap(dtm, "@1h") == snap(dtm, "@h")

    @pytest.mark.parametrize("snaptime", ["@7m", "@2d", "@0m", "@5h", "@2w", "@2mon", "@2q", "@2y"])
    def test_snap_multiple_invalid(self, dtm: pendulum.DateTime, snaptime: str):
        # act/assert
        with pytest.raises(SnaptimeError, match="Snaptime string is invalid"):
            snap(dtm, snaptime)

    @pytest.mark.parametrize("tz", [None, ZoneInfo("America/New_York"), timezone.utc])
    def test_snap_multiple_datetime(self, tz: tzinfo | None):
        # arrange
        dtm = datetime(2024, 12, 30, 18, 52, 37, 123456, tzinfo=tz)

        # act
        result = snap(dtm, "@15m")

        # assert
        assert type(result) is datetime
        assert result.tzinfo is tz
        assert result == datetime(2024, 12, 30, 18, 45, tzinfo=tz)

    @pytest.mark.parametrize(
        "fold,utcoffset",
        [(0, timedelta(hours=1)), (1, timedelta(0))],
    )
    def test_snap_multiple_pendulum_across_dst(self, fold: int, utcoffset: timedelta):
        # arrange
        dtm = pendulum.datetime(2024, 10, 27, 1, 52, tz="Europe/London", fold=fold)

        # act
        result = snap(dtm, "@15m")

        # assert
        assert type(result) is pendulum.DateTime
        assert result.naive() == pendulum.naive(2024, 10, 27, 1, 45)
        assert result.utcoffset() == utcoffset

    @pytest.mark.parametrize(
        "fold,utcoffset",
        [(0, timedelta(hours=1)), (1, timedelta(0))],
    )
    def test_snap_multiple_datetime_across_dst(self, fold: int, utcoffset: timedelta):
        # arrange
        tz = ZoneInfo("Europe/London")
        dtm = datetime(2024, 10, 27, 1, 52, tzinfo=tz, fold=fold)

        # act
        result = snap(dtm, "@15m")

        # assert
        assert type(result) is datetime
        assert result.tzinfo is tz
        assert result.replace(tzinfo=None) == datetime(2024, 10, 27, 1, 45)
        assert result.utcoffset() == utcoffset


class TestApply:
    @pytest.mark.parametrize(
        "dtm,expected_type",
        [
            (pendulum.datetime(2024, 12, 30, 13, 1, 10, 999999), pendulum.DateTime),
            (pendulum.datetime(2024, 12, 30, 13, 1, 10, 999999, tz="Europe/London"), pendulum.DateTime),
            (datetime(2024, 12, 30, 13, 1, 10, 999999), datetime),
            (datetime(2024, 12, 30, 13, 1, 10, 999999, tzinfo=ZoneInfo("America/New_York")), datetime),
        ],
        ids=["pendulum", "pendulum_timezone", "datetime_naive", "datetime_aware"],
    )
    def test_apply_matches_snap(self, dtm: datetime, expected_type: type[datetime]):
        # act
        result = apply(dtm, parse("@d-2h+10m"))

        # assert
        assert result == snap(dtm, "@d-2h+10m")
        assert type(result) is expected_type
        assert result.tzinfo is dtm.tzinfo

    @pytest.mark.parametrize(
        "dtm,snap_dtm,expected_type",
        [
            (
                pendulum.datetime(2024, 12, 30, 18, 52, 37, 123456),
                pendulum.datetime(2024, 12, 30, 18, 45),
                pendulum.DateTime,
            ),
            (datetime(2024, 12, 30, 18, 52, 37, 123456), datetime(2024, 12, 30, 18, 45), datetime),
            (
                datetime(2024, 12, 30, 18, 52, 37, 123456, tzinfo=ZoneInfo("Europe/London")),
                datetime(2024, 12, 30, 18, 45, tzinfo=ZoneInfo("Europe/London")),
                datetime,
            ),
        ],
        ids=["pendulum", "datetime_naive", "datetime_aware"],
    )
    def test_apply_snap_multiple(self, dtm: datetime, snap_dtm: datetime, expected_type: type[datetime]):
        # arrange
        snaptimes = parse("@15m")

        # act
        result = apply(dtm, snaptimes)

        # assert
        assert snaptimes == [Snaptime(action=Action.SNAP, unit=Unit.MINUTE, time_int=15)]
        assert result == snap_dtm
        assert result == snap(dtm, "@15m")
        assert type(result) is expected_type
        assert result.tzinfo is dtm.tzinfo

    @pytest.mark.parametrize(
        "dtm,snap_dtm,expected_type",
        [
            (pendulum.datetime(2024, 12, 30, 18, 52), pendulum.datetime(2024, 12, 29, 22, 10), pendulum.DateTime),
            (datetime(2024, 12, 30, 18, 52), datetime(2024, 12, 29, 22, 10), datetime),
            (
                datetime(2024, 12, 30, 18, 52, tzinfo=ZoneInfo("Europe/London")),
                datetime(2024, 12, 29, 22, 10, tzinfo=ZoneInfo("Europe/London")),
                datetime,
            ),
        ],
        ids=["pendulum", "datetime_naive", "datetime_aware"],
    )
    def test_apply_snaptimes_without_string(self, dtm: datetime, snap_dtm: datetime, expected_type: type[datetime]):
        # arrange
        snaptimes = (
            Snaptime(action=Action.SNAP, unit=Unit.DAY),
            Snaptime(action=Action.SUB, unit=Unit.HOUR, time_int=2),
            Snaptime(action=Action.ADD, unit=Unit.MINUTE, time_int=10),
        )

        # act
        result = apply(dtm, snaptimes)

        # assert
        assert result == snap_dtm
        assert type(result) is expected_type

    def test_apply_parsed_snaptimes_many_times(self):
        # arrange
        snaptimes = parse("@d-2h")
        tz = ZoneInfo("Europe/London")
        dtms = [
            pendulum.datetime(2024, 12, 30, 18, 52),
            datetime(2025, 3, 1, 0, 30),
            datetime(2025, 3, 1, 0, 30, tzinfo=tz),
        ]

        # act
        results = [apply(dtm, snaptimes) for dtm in dtms]

        # assert
        assert results == [
            pendulum.datetime(2024, 12, 29, 22, 0),
            datetime(2025, 2, 28, 22, 0),
            datetime(2025, 2, 28, 22, 0, tzinfo=tz),
        ]
        assert [type(result) for result in results] == [pendulum.DateTime, datetime, datetime]

    @pytest.mark.parametrize(
        "dtm,expected_type",
        [
            (pendulum.datetime(2024, 12, 30, 13, 1, 10, 999999), pendulum.DateTime),
            (datetime(2024, 12, 30, 13, 1, 10, 999999), datetime),
            (datetime(2024, 12, 30, 13, 1, 10, 999999, tzinfo=ZoneInfo("America/New_York")), datetime),
        ],
        ids=["pendulum", "datetime_naive", "datetime_aware"],
    )
    def test_apply_no_snaptimes(self, dtm: datetime, expected_type: type[datetime]):
        # act
        result = apply(dtm, [])

        # assert
        assert result == dtm
        assert type(result) is expected_type
        assert result.tzinfo is dtm.tzinfo

    def test_apply_invalid_datetime(self):
        # arrange
        dtm = "2024-12-30"

        # act/assert
        with pytest.raises(
            TypeError,
            match=re.escape(
                "Invalid datetime type. Must be pendulum.DateTime, datetime.datetime, pendulum.Date or datetime.date."
            ),
        ):
            apply(dtm, parse("@d"))

    def test_apply_exported_from_package(self):
        # assert
        assert python_snaptime.apply is apply
        assert "apply" in python_snaptime.__all__

    @pytest.mark.parametrize(
        "dtm",
        [
            pendulum.datetime(2024, 12, 31, 13, 1, 10),
            pendulum.datetime(2024, 12, 31, 13, 1, 10, tz="America/New_York"),
            datetime(2024, 12, 31, 13, 1, 10),
            datetime(2024, 12, 31, 13, 1, 10, tzinfo=ZoneInfo("America/New_York")),
        ],
        ids=["pendulum", "pendulum_timezone", "datetime_naive", "datetime_aware"],
    )
    @pytest.mark.parametrize(
        "week_start,day",
        [(None, 30), (Weekday.MONDAY, 30), (Weekday.SUNDAY, 29), (Weekday.TUESDAY, 31)],
        ids=["default", "monday", "sunday", "tuesday"],
    )
    def test_apply_week_start(self, dtm: datetime, week_start: Weekday | None, day: int):
        # arrange
        snaptimes = parse("@w")

        # act
        result = apply(dtm, snaptimes) if week_start is None else apply(dtm, snaptimes, week_start=week_start)

        # assert
        assert type(result) is type(dtm)
        assert result == dtm.replace(day=day, hour=0, minute=0, second=0)
        assert result.utcoffset() == dtm.utcoffset()


class TestSnapRange:
    @pytest.mark.parametrize(
        "dtm",
        [
            pendulum.datetime(2024, 12, 30, 18),
            pendulum.datetime(2024, 12, 30, 18, tz=pendulum.timezone("America/New_York")),
            datetime(2024, 12, 30, 18),
            datetime(2024, 12, 30, 18, tzinfo=ZoneInfo("America/New_York")),
            datetime(2024, 12, 30, 18, tzinfo=timezone(timedelta(hours=5, minutes=30))),
        ],
    )
    @pytest.mark.parametrize(
        "start,end,inclusive,start_delta,end_delta",
        [
            ("-1d@d", "@d", False, timedelta(days=-1), timedelta(0)),
            ("-1d@d", "@d", True, timedelta(days=-1), timedelta(microseconds=-1)),
            ("@d", "@d", False, timedelta(0), timedelta(0)),
            ("@d", "@d+1us", True, timedelta(0), timedelta(0)),
        ],
    )
    def test_snap_range(
        self,
        dtm: datetime,
        start: str,
        end: str,
        inclusive: bool,
        start_delta: timedelta,
        end_delta: timedelta,
    ):
        # arrange
        midnight = dtm.replace(hour=0)

        # act
        result = snap_range(dtm, start, end, inclusive=inclusive)

        # assert
        assert result == (midnight + start_delta, midnight + end_delta)
        assert type(result) is tuple
        assert len(result) == 2
        for result_dtm in result:
            assert type(result_dtm) is type(dtm)
            assert result_dtm.tzinfo is dtm.tzinfo

    def test_snap_range_pendulum(self):
        # arrange
        dtm = pendulum.datetime(2024, 12, 30, 18)

        # act
        result = snap_range(dtm, "-1d@d", "@d", inclusive=True)

        # assert
        assert result == (pendulum.datetime(2024, 12, 29), pendulum.datetime(2024, 12, 29, 23, 59, 59, 999999))
        assert all(type(result_dtm) is pendulum.DateTime for result_dtm in result)
        assert all(result_dtm.tzinfo == pendulum.UTC for result_dtm in result)

    @pytest.mark.parametrize(
        "tz",
        [None, ZoneInfo("America/New_York"), timezone.utc, timezone(timedelta(hours=5, minutes=30))],
    )
    def test_snap_range_datetime(self, tz: tzinfo | None):
        # arrange
        dtm = datetime(2024, 12, 30, 18, tzinfo=tz)

        # act
        result = snap_range(dtm, "-1d@d", "@d", inclusive=True)

        # assert
        assert result == (datetime(2024, 12, 29, tzinfo=tz), datetime(2024, 12, 29, 23, 59, 59, 999999, tzinfo=tz))
        assert all(type(result_dtm) is datetime for result_dtm in result)
        assert all(result_dtm.tzinfo is tz for result_dtm in result)

    @pytest.mark.parametrize("dtm", [pendulum.datetime(2024, 12, 30, 18), datetime(2024, 12, 30, 18)])
    def test_snap_range_empty_inclusive(self, dtm: datetime):
        # act/assert
        with pytest.raises(
            SnaptimeError,
            match=re.escape("The range from '@d' to '@d' is empty. An inclusive range must not be empty."),
        ):
            snap_range(dtm, "@d", "@d", inclusive=True)

    @pytest.mark.parametrize("dtm", [pendulum.datetime(2024, 12, 30, 18), datetime(2024, 12, 30, 18)])
    @pytest.mark.parametrize("inclusive", [False, True])
    def test_snap_range_reversed(self, dtm: datetime, inclusive: bool):
        # act/assert
        with pytest.raises(SnaptimeError, match=re.escape("The start of the range ('@d') is after the end ('-1d@d').")):
            snap_range(dtm, "@d", "-1d@d", inclusive=inclusive)

    def test_snap_range_invalid_datetime(self):
        # act/assert
        with pytest.raises(TypeError, match=re.escape("Invalid datetime type.")):
            snap_range("2024-12-30", "-1d@d", "@d")

    @pytest.mark.parametrize(
        "dtm",
        [
            pendulum.datetime(2024, 12, 31, 18),
            pendulum.datetime(2024, 12, 31, 18, tz="America/New_York"),
            datetime(2024, 12, 31, 18),
            datetime(2024, 12, 31, 18, tzinfo=ZoneInfo("America/New_York")),
        ],
        ids=["pendulum", "pendulum_timezone", "datetime_naive", "datetime_aware"],
    )
    @pytest.mark.parametrize(
        "inclusive,end_delta",
        [(False, timedelta(0)), (True, timedelta(microseconds=-1))],
    )
    def test_snap_range_week_start(self, dtm: datetime, inclusive: bool, end_delta: timedelta):
        # arrange
        sunday = dtm.replace(day=29, hour=0)

        # act
        result = snap_range(dtm, "@w-1w", "@w", inclusive=inclusive, week_start=Weekday.SUNDAY)

        # assert
        assert result == (sunday - timedelta(weeks=1), sunday + end_delta)
        for result_dtm in result:
            assert type(result_dtm) is type(dtm)
            assert result_dtm.tzinfo == dtm.tzinfo

    def test_snap_range_week_start_default_is_monday(self):
        # act
        result = snap_range(pendulum.datetime(2024, 12, 31, 18), "@w-1w", "@w")

        # assert
        assert result == (pendulum.datetime(2024, 12, 23), pendulum.datetime(2024, 12, 30))
        assert all(type(result_dtm) is pendulum.DateTime for result_dtm in result)

    @pytest.mark.parametrize("end", ["now", NOW])
    def test_snap_range_now_end_pendulum(self, end: str):
        # arrange
        dtm = pendulum.datetime(2024, 12, 30, 18, 52)

        # act
        result = snap_range(dtm, "-24h", end)

        # assert
        assert result == (pendulum.datetime(2024, 12, 29, 18, 52), pendulum.datetime(2024, 12, 30, 18, 52))
        assert all(type(result_dtm) is pendulum.DateTime for result_dtm in result)

    @pytest.mark.parametrize(
        "dtm,expected_type",
        [
            (pendulum.datetime(2024, 12, 30, 18, 52, 30, 123456), pendulum.DateTime),
            (pendulum.datetime(2024, 12, 30, 18, 52, 30, 123456, tz="America/New_York"), pendulum.DateTime),
            (datetime(2024, 12, 30, 18, 52, 30, 123456), datetime),
            (datetime(2024, 12, 30, 18, 52, 30, 123456, tzinfo=ZoneInfo("America/New_York")), datetime),
        ],
        ids=["pendulum", "pendulum_timezone", "datetime_naive", "datetime_aware"],
    )
    @pytest.mark.parametrize(
        "start,end,inclusive,start_delta,end_delta",
        [
            ("-24h", "now", False, timedelta(hours=-24), timedelta(0)),
            ("-24h", NOW, True, timedelta(hours=-24), timedelta(microseconds=-1)),
            ("now", "+1h", False, timedelta(0), timedelta(hours=1)),
            (NOW, "+1h", True, timedelta(0), timedelta(hours=1, microseconds=-1)),
            ("now", "now", False, timedelta(0), timedelta(0)),
        ],
    )
    def test_snap_range_now(
        self,
        dtm: datetime,
        expected_type: type[datetime],
        start: str,
        end: str,
        inclusive: bool,
        start_delta: timedelta,
        end_delta: timedelta,
    ):
        # act
        result = snap_range(dtm, start, end, inclusive=inclusive)

        # assert
        assert result == (dtm + start_delta, dtm + end_delta)
        for result_dtm in result:
            assert type(result_dtm) is expected_type
            assert result_dtm.tzinfo is dtm.tzinfo

    @pytest.mark.parametrize("dtm", [pendulum.datetime(2024, 12, 30, 18), datetime(2024, 12, 30, 18)])
    def test_snap_range_now_empty_inclusive(self, dtm: datetime):
        # act/assert
        with pytest.raises(
            SnaptimeError,
            match=re.escape("The range from 'now' to 'now' is empty. An inclusive range must not be empty."),
        ):
            snap_range(dtm, "now", "now", inclusive=True)

    @pytest.mark.parametrize("dtm", [pendulum.datetime(2024, 12, 30, 18), datetime(2024, 12, 30, 18)])
    def test_snap_range_now_reversed(self, dtm: datetime):
        # act/assert
        with pytest.raises(SnaptimeError, match=re.escape("The start of the range ('now') is after the end ('-1h').")):
            snap_range(dtm, "now", "-1h")


class TestSnapNow:
    @pytest.fixture(autouse=True)
    def frozen_now(self, monkeypatch: pytest.MonkeyPatch):
        frozen = pendulum.datetime(2024, 12, 30, 18, 52, 30, 123456, tz="UTC")
        monkeypatch.setattr(pendulum, "now", lambda tz=None: frozen.in_timezone(tz))

    def test_snap_now_default_timezone_is_utc(self):
        # act
        result = snap_now("@d")

        # assert
        assert type(result) is pendulum.DateTime
        assert result == pendulum.datetime(2024, 12, 30, tz="UTC")
        assert result.timezone_name == "UTC"

    def test_snap_now_timezone_string(self):
        # act
        result = snap_now("@h", tz="Europe/London")

        # assert
        assert type(result) is pendulum.DateTime
        assert result == pendulum.datetime(2024, 12, 30, 18, tz="Europe/London")
        assert result.timezone_name == "Europe/London"

    @pytest.mark.parametrize(
        "tz,snaptime,snap_dtm",
        [
            ("Asia/Tokyo", "@d", pendulum.datetime(2024, 12, 31, tz="Asia/Tokyo")),
            (
                pendulum.timezone("America/New_York"),
                "@d-2h",
                pendulum.datetime(2024, 12, 29, 22, tz="America/New_York"),
            ),
            (pendulum.timezone(-36000), "@m+5m", pendulum.datetime(2024, 12, 30, 8, 57, tz=pendulum.timezone(-36000))),
        ],
    )
    def test_snap_now_pendulum_timezone(self, tz: str | tzinfo, snaptime: str, snap_dtm: pendulum.DateTime):
        # act
        result = snap_now(snaptime, tz=tz)

        # assert
        assert type(result) is pendulum.DateTime
        assert result == snap_dtm
        assert result.utcoffset() == snap_dtm.utcoffset()

    @pytest.mark.parametrize(
        "tz,snaptime,snap_dtm",
        [
            (ZoneInfo("Asia/Tokyo"), "@d", datetime(2024, 12, 31, tzinfo=ZoneInfo("Asia/Tokyo"))),
            (ZoneInfo("America/New_York"), "@d-2h", datetime(2024, 12, 29, 22, tzinfo=ZoneInfo("America/New_York"))),
            (
                timezone(timedelta(hours=-10)),
                "@m+5m",
                datetime(2024, 12, 30, 8, 57, tzinfo=timezone(timedelta(hours=-10))),
            ),
            (timezone.utc, "@h", datetime(2024, 12, 30, 18, tzinfo=timezone.utc)),
        ],
    )
    def test_snap_now_datetime_timezone(self, tz: tzinfo, snaptime: str, snap_dtm: datetime):
        # act
        result = snap_now(snaptime, tz=tz)

        # assert
        assert type(result) is datetime
        assert result == snap_dtm
        assert result.utcoffset() == snap_dtm.utcoffset()
        assert result.tzinfo is tz

    @pytest.mark.parametrize(
        "tz,week_start,snap_dtm",
        [
            (None, Weekday.SATURDAY, pendulum.datetime(2024, 12, 28, tz="UTC")),
            ("America/New_York", Weekday.SUNDAY, pendulum.datetime(2024, 12, 29, tz="America/New_York")),
            ("Asia/Tokyo", Weekday.TUESDAY, pendulum.datetime(2024, 12, 31, tz="Asia/Tokyo")),
        ],
    )
    def test_snap_now_week_start_pendulum(self, tz: str | None, week_start: Weekday, snap_dtm: pendulum.DateTime):
        # act
        result = snap_now("@w", tz=tz, week_start=week_start)

        # assert
        assert type(result) is pendulum.DateTime
        assert result == snap_dtm
        assert result.timezone_name == snap_dtm.timezone_name

    @pytest.mark.parametrize(
        "tz,week_start,snap_dtm",
        [
            (ZoneInfo("America/New_York"), Weekday.SUNDAY, datetime(2024, 12, 29, tzinfo=ZoneInfo("America/New_York"))),
            (ZoneInfo("Asia/Tokyo"), Weekday.TUESDAY, datetime(2024, 12, 31, tzinfo=ZoneInfo("Asia/Tokyo"))),
            (timezone.utc, Weekday.SATURDAY, datetime(2024, 12, 28, tzinfo=timezone.utc)),
        ],
    )
    def test_snap_now_week_start_datetime(self, tz: tzinfo, week_start: Weekday, snap_dtm: datetime):
        # act
        result = snap_now("@w", tz=tz, week_start=week_start)

        # assert
        assert type(result) is datetime
        assert result == snap_dtm
        assert result.tzinfo is tz

    def test_snap_now_week_start_default_is_monday(self):
        # act
        result = snap_now("@w", tz=ZoneInfo("Asia/Tokyo"))

        # assert
        assert type(result) is datetime
        assert result == datetime(2024, 12, 30, tzinfo=ZoneInfo("Asia/Tokyo"))

    @pytest.mark.parametrize("snaptime", ["now", NOW])
    def test_snap_now_now_keyword_pendulum(self, snaptime: str):
        # act
        result = snap_now(snaptime, tz="Europe/London")

        # assert
        assert type(result) is pendulum.DateTime
        assert result == pendulum.datetime(2024, 12, 30, 18, 52, 30, 123456, tz="UTC")
        assert result.timezone_name == "Europe/London"

    @pytest.mark.parametrize("snaptime", ["now", NOW])
    def test_snap_now_now_keyword_datetime(self, snaptime: str):
        # arrange
        tz = ZoneInfo("Asia/Tokyo")

        # act
        result = snap_now(snaptime, tz=tz)

        # assert
        assert type(result) is datetime
        assert result == datetime(2024, 12, 31, 3, 52, 30, 123456, tzinfo=tz)
        assert result.tzinfo is tz


class TestCompile:
    @pytest.mark.parametrize(
        "dtm,snap_dtm,expected_type",
        [
            (pendulum.datetime(2024, 12, 30, 18, 52), pendulum.datetime(2024, 12, 29), pendulum.DateTime),
            (
                pendulum.datetime(2024, 12, 30, 18, 52, tz="Europe/London"),
                pendulum.datetime(2024, 12, 29, tz="Europe/London"),
                pendulum.DateTime,
            ),
            (datetime(2024, 12, 30, 18, 52), datetime(2024, 12, 29), datetime),
            (
                datetime(2024, 12, 30, 18, 52, tzinfo=ZoneInfo("America/New_York")),
                datetime(2024, 12, 29, tzinfo=ZoneInfo("America/New_York")),
                datetime,
            ),
        ],
        ids=["pendulum", "pendulum_timezone", "datetime_naive", "datetime_aware"],
    )
    def test_compile_apply_matches_snap(self, dtm: datetime, snap_dtm: datetime, expected_type: type[datetime]):
        # act
        result = compile("-1d@d").apply(dtm)

        # assert
        assert result == snap_dtm
        assert result == snap(dtm, "-1d@d")
        assert type(result) is expected_type
        assert result.tzinfo is dtm.tzinfo

    def test_compile_apply_many_times(self):
        # arrange
        compiled = compile("@d-2h")
        tz = ZoneInfo("Europe/London")
        dtms = [
            pendulum.datetime(2024, 12, 30, 18, 52),
            datetime(2025, 3, 1, 0, 30),
            datetime(2025, 3, 1, 0, 30, tzinfo=tz),
        ]

        # act
        results = [compiled.apply(dtm) for dtm in dtms]

        # assert
        assert results == [
            pendulum.datetime(2024, 12, 29, 22, 0),
            datetime(2025, 2, 28, 22, 0),
            datetime(2025, 2, 28, 22, 0, tzinfo=tz),
        ]
        assert [type(result) for result in results] == [pendulum.DateTime, datetime, datetime]

    def test_compile_snaptimes(self):
        # act
        compiled = compile("@d-2h")

        # assert
        assert compiled.snaptimes == (
            Snaptime(action=Action.SNAP, unit=Unit.DAY),
            Snaptime(action=Action.SUB, unit=Unit.HOUR, time_int=2),
        )

    @pytest.mark.parametrize(
        "snaptime,result",
        [
            ("@d-2h", "@d-2h"),
            ("@days-2hours+10minutes", "@d-2h+10m"),
            ("@15m", "@15m"),
            ("now", "now"),
            (NOW, "now"),
        ],
    )
    def test_compile_str(self, snaptime: str, result: str):
        # act/assert
        assert str(compile(snaptime)) == result

    @pytest.mark.parametrize("snaptime", ["@ms", "@d-h", "", "@d 2h", "now-1d", "NOW", "now()"])
    def test_compile_invalid(self, snaptime: str):
        # act/assert
        with pytest.raises(SnaptimeError, match="Snaptime string is invalid"):
            compile(snaptime)

    @pytest.mark.parametrize(
        "dtm,expected_type",
        [
            (pendulum.datetime(2024, 12, 30, 18, 52, 30, 123456), pendulum.DateTime),
            (pendulum.datetime(2024, 12, 30, 18, 52, 30, 123456, tz="America/New_York"), pendulum.DateTime),
            (datetime(2024, 12, 30, 18, 52, 30, 123456), datetime),
            (datetime(2024, 12, 30, 18, 52, 30, 123456, tzinfo=ZoneInfo("America/New_York")), datetime),
        ],
        ids=["pendulum", "pendulum_timezone", "datetime_naive", "datetime_aware"],
    )
    def test_compile_now(self, dtm: datetime, expected_type: type[datetime]):
        # act
        compiled = compile("now")
        result = compiled.apply(dtm)

        # assert
        assert compiled.snaptimes == ()
        assert result == dtm
        assert type(result) is expected_type
        assert result.tzinfo is dtm.tzinfo

    def test_compile_equal_and_hashable(self):
        # act
        first = compile("@d-2h")
        second = compile("@day-2hours")

        # assert
        assert first == second
        assert hash(first) == hash(second)
        assert first != compile("@d")

    @pytest.mark.parametrize(
        "dtm,snap_dtm,expected_type",
        [
            (pendulum.datetime(2024, 12, 31, 13, 1, 10), pendulum.datetime(2024, 12, 29), pendulum.DateTime),
            (
                pendulum.datetime(2024, 12, 31, 13, 1, 10, tz="America/New_York"),
                pendulum.datetime(2024, 12, 29, tz="America/New_York"),
                pendulum.DateTime,
            ),
            (datetime(2024, 12, 31, 13, 1, 10), datetime(2024, 12, 29), datetime),
            (
                datetime(2024, 12, 31, 13, 1, 10, tzinfo=ZoneInfo("America/New_York")),
                datetime(2024, 12, 29, tzinfo=ZoneInfo("America/New_York")),
                datetime,
            ),
        ],
        ids=["pendulum", "pendulum_timezone", "datetime_naive", "datetime_aware"],
    )
    def test_compile_week_start(self, dtm: datetime, snap_dtm: datetime, expected_type: type[datetime]):
        # act
        result = compile("@w", week_start=Weekday.SUNDAY).apply(dtm)

        # assert
        assert result == snap_dtm
        assert result == snap(dtm, "@w", week_start=Weekday.SUNDAY)
        assert type(result) is expected_type
        assert result.tzinfo is dtm.tzinfo

    @pytest.mark.parametrize(
        "dtm,expected_type",
        [
            (pendulum.datetime(2024, 12, 31, 13, 1, 10), pendulum.DateTime),
            (datetime(2024, 12, 31, 13, 1, 10), datetime),
            (datetime(2024, 12, 31, 13, 1, 10, tzinfo=ZoneInfo("America/New_York")), datetime),
        ],
        ids=["pendulum", "datetime_naive", "datetime_aware"],
    )
    @pytest.mark.parametrize(
        "compile_week_start,apply_week_start,day",
        [
            (None, None, 30),
            (Weekday.SUNDAY, None, 29),
            (None, Weekday.SUNDAY, 29),
            (Weekday.SUNDAY, Weekday.TUESDAY, 31),
            (Weekday.SUNDAY, Weekday.MONDAY, 30),
        ],
        ids=["default", "compile", "apply", "apply_overrides_compile", "apply_monday_overrides_compile"],
    )
    def test_compile_apply_week_start(
        self,
        dtm: datetime,
        expected_type: type[datetime],
        compile_week_start: Weekday | None,
        apply_week_start: Weekday | None,
        day: int,
    ):
        # arrange
        compiled = compile("@w") if compile_week_start is None else compile("@w", week_start=compile_week_start)

        # act
        result = compiled.apply(dtm, week_start=apply_week_start)

        # assert
        assert result == dtm.replace(day=day, hour=0, minute=0, second=0)
        assert type(result) is expected_type

    def test_compile_week_start_equality(self):
        # act/assert
        assert compile("@w").week_start is Weekday.MONDAY
        assert CompiledSnaptime(()).week_start is Weekday.MONDAY
        assert compile("@w") == compile("@w", week_start=Weekday.MONDAY)
        assert compile("@w") != compile("@w", week_start=Weekday.SUNDAY)
        assert str(compile("@w", week_start=Weekday.SUNDAY)) == "@w"

    def test_compile_immutable(self):
        # arrange
        compiled = compile("@d")

        # act/assert
        with pytest.raises(FrozenInstanceError):
            compiled.snaptimes = ()

    def test_compile_repr(self):
        # act/assert
        assert repr(compile("@d")) == (
            "CompiledSnaptime(snaptimes=(Snaptime(action=<Action.SNAP: '@'>, unit=<Unit.DAY: ('d', 'day', 'days')>, "
            "time_int=None, weekday=None),), week_start=<Weekday.MONDAY: 0>)"
        )

    def test_compiled_snaptime_converts_list_to_tuple(self):
        # arrange
        snaptimes = [Snaptime(action=Action.SNAP, unit=Unit.DAY)]

        # act
        compiled = CompiledSnaptime(snaptimes)

        # assert
        assert compiled.snaptimes == (Snaptime(action=Action.SNAP, unit=Unit.DAY),)
        assert compiled.apply(datetime(2024, 12, 30, 18, 52)) == datetime(2024, 12, 30)

    def test_compiled_snaptime_no_snaptimes(self):
        # arrange
        dtm = pendulum.datetime(2024, 12, 30, 18, 52)

        # act
        result = CompiledSnaptime(()).apply(dtm)

        # assert
        assert result == dtm
        assert type(result) is pendulum.DateTime
        assert str(CompiledSnaptime(())) == "now"

    def test_compile_apply_invalid_datetime(self):
        # arrange
        dtm = "2024-12-30"

        # act/assert
        with pytest.raises(
            TypeError,
            match=re.escape(
                "Invalid datetime type. Must be pendulum.DateTime, datetime.datetime, pendulum.Date or datetime.date."
            ),
        ):
            compile("@d").apply(dtm)

    def test_compile_exported_from_package(self):
        # assert
        assert python_snaptime.compile is compile
        assert python_snaptime.CompiledSnaptime is CompiledSnaptime
        assert "compile" in python_snaptime.__all__
        assert "CompiledSnaptime" in python_snaptime.__all__


DATE_TYPES = pytest.mark.parametrize("date_type", [date, pendulum.Date], ids=["date", "pendulum_date"])


@DATE_TYPES
class TestDate:
    @pytest.mark.parametrize(
        "snaptime,snap_date",
        [
            ("@d", (2024, 12, 30)),
            ("-1d", (2024, 12, 29)),
            ("+2days", (2025, 1, 1)),
            ("+0d", (2024, 12, 30)),
            ("@w", (2024, 12, 30)),
            ("-1w", (2024, 12, 23)),
            ("+1week", (2025, 1, 6)),
            ("@mon", (2024, 12, 1)),
            ("-1mon", (2024, 11, 30)),
            ("+2months", (2025, 2, 28)),
            ("@q", (2024, 10, 1)),
            ("-1q", (2024, 9, 30)),
            ("+1quarter", (2025, 3, 30)),
            ("@y", (2024, 1, 1)),
            ("-1y", (2023, 12, 30)),
            ("+1year", (2025, 12, 30)),
            ("-1mon@mon", (2024, 11, 1)),
            ("@w-2d@d", (2024, 12, 28)),
            ("@q+2mon@mon-1w@w", (2024, 11, 18)),
            ("@y-1d@w+3d", (2023, 12, 28)),
        ],
    )
    def test_snap_date(self, date_type: type[date], snaptime: str, snap_date: tuple[int, int, int]):
        # arrange
        dtm = date_type(2024, 12, 30)

        # act
        result = snap(dtm, snaptime)

        # assert
        assert result == date(*snap_date)
        assert type(result) is date_type

    def test_snap_date_leap_day(self, date_type: type[date]):
        # act
        result = snap(date_type(2024, 2, 29), "+1y")

        # assert
        assert result == date(2025, 2, 28)
        assert type(result) is date_type

    @pytest.mark.parametrize(
        "week_start,snap_date",
        [
            (Weekday.MONDAY, (2024, 12, 30)),
            (Weekday.WEDNESDAY, (2024, 12, 25)),
            (Weekday.SUNDAY, (2024, 12, 29)),
        ],
    )
    def test_snap_date_week_start(self, date_type: type[date], week_start: Weekday, snap_date: tuple[int, int, int]):
        # act
        result = snap(date_type(2024, 12, 31), "@w", week_start=week_start)

        # assert
        assert result == date(*snap_date)
        assert type(result) is date_type

    @pytest.mark.parametrize(
        "snaptime,rejected,unit",
        [
            ("@s", "@s", "s"),
            ("@m", "@m", "m"),
            ("@h", "@h", "h"),
            ("@15m", "@15m", "m"),
            ("+1us", "+1us", "us"),
            ("-1ms", "-1ms", "ms"),
            ("+30secs", "+30s", "s"),
            ("-1m", "-1m", "m"),
            ("-24hours", "-24h", "h"),
            ("@d-2h", "-2h", "h"),
            ("-1mon@mon+0h", "+0h", "h"),
        ],
    )
    def test_snap_date_rejects_unit_smaller_than_day(
        self, date_type: type[date], snaptime: str, rejected: str, unit: str
    ):
        # arrange
        msg = f"Cannot apply {rejected!r} to a date: the unit {unit!r} is smaller than a day."

        # act/assert
        with pytest.raises(SnaptimeError, match=re.escape(msg)):
            snap(date_type(2024, 12, 30), snaptime)

    def test_apply_date(self, date_type: type[date]):
        # arrange
        operations = [
            Snaptime(action=Action.SUB, unit=Unit.MONTH, time_int=1),
            Snaptime(action=Action.SNAP, unit=Unit.MONTH),
        ]

        # act
        result = apply(date_type(2024, 12, 30), operations)

        # assert
        assert result == date(2024, 11, 1)
        assert type(result) is date_type

    def test_apply_date_no_snaptimes(self, date_type: type[date]):
        # act
        result = apply(date_type(2024, 12, 30), [])

        # assert
        assert result == date(2024, 12, 30)
        assert type(result) is date_type

    def test_apply_date_rejects_unit_smaller_than_day(self, date_type: type[date]):
        # arrange
        operations = [
            Snaptime(action=Action.SNAP, unit=Unit.DAY),
            Snaptime(action=Action.ADD, unit=Unit.HOUR, time_int=6),
        ]

        # act/assert
        with pytest.raises(SnaptimeError, match=re.escape("Cannot apply '+6h' to a date")):
            apply(date_type(2024, 12, 30), operations)

    @pytest.mark.parametrize("week_start,day", [(None, 23), (Weekday.SUNDAY, 22)])
    def test_compile_apply_date(self, date_type: type[date], week_start: Weekday | None, day: int):
        # arrange
        compiled = compile("-1w@w", week_start=Weekday.MONDAY)

        # act
        result = compiled.apply(date_type(2024, 12, 30), week_start=week_start)

        # assert
        assert result == date(2024, 12, day)
        assert type(result) is date_type

    def test_compile_apply_date_rejects_unit_smaller_than_day(self, date_type: type[date]):
        # act/assert
        with pytest.raises(SnaptimeError, match=re.escape("Cannot apply '@h' to a date")):
            compile("@d@h").apply(date_type(2024, 12, 30))

    @pytest.mark.parametrize(
        "start,end,inclusive,range_dates",
        [
            ("-1w@w", "@w", False, ((2024, 12, 23), (2024, 12, 30))),
            ("-1w@w", "@w", True, ((2024, 12, 23), (2024, 12, 29))),
            ("-1d", "@d", False, ((2024, 12, 29), (2024, 12, 30))),
            ("-1d", "@d", True, ((2024, 12, 29), (2024, 12, 29))),
            ("@mon", "+1mon@mon", True, ((2024, 12, 1), (2024, 12, 31))),
            ("@y", "+1y@y", True, ((2024, 1, 1), (2024, 12, 31))),
            ("@d", "@d", False, ((2024, 12, 30), (2024, 12, 30))),
        ],
    )
    def test_snap_range_date(
        self,
        date_type: type[date],
        start: str,
        end: str,
        inclusive: bool,
        range_dates: tuple[tuple[int, int, int], tuple[int, int, int]],
    ):
        # act
        result = snap_range(date_type(2024, 12, 30), start, end, inclusive=inclusive)

        # assert
        assert result == (date(*range_dates[0]), date(*range_dates[1]))
        assert type(result) is tuple
        assert all(type(result_date) is date_type for result_date in result)

    def test_snap_range_date_week_start(self, date_type: type[date]):
        # act
        result = snap_range(date_type(2024, 12, 31), "@w-1w", "@w", inclusive=True, week_start=Weekday.SUNDAY)

        # assert
        assert result == (date(2024, 12, 22), date(2024, 12, 28))
        assert all(type(result_date) is date_type for result_date in result)

    def test_snap_range_date_empty_inclusive(self, date_type: type[date]):
        # act/assert
        with pytest.raises(SnaptimeError, match=re.escape("The range from '@d' to '@d' is empty.")):
            snap_range(date_type(2024, 12, 30), "@d", "@d", inclusive=True)

    @pytest.mark.parametrize("inclusive", [False, True])
    def test_snap_range_date_reversed(self, date_type: type[date], inclusive: bool):
        # act/assert
        with pytest.raises(SnaptimeError, match=re.escape("The start of the range ('@d') is after the end ('-1d').")):
            snap_range(date_type(2024, 12, 30), "@d", "-1d", inclusive=inclusive)

    def test_snap_range_date_rejects_unit_smaller_than_day(self, date_type: type[date]):
        # act/assert
        with pytest.raises(SnaptimeError, match=re.escape("Cannot apply '-12h' to a date")):
            snap_range(date_type(2024, 12, 30), "-1d", "@d-12h")


@pytest.mark.parametrize("snaptime", ["now", NOW])
@pytest.mark.parametrize(
    "dtm,expected_type",
    [(date(2024, 12, 30), date), (pendulum.date(2024, 12, 30), pendulum.Date)],
    ids=["date", "pendulum_date"],
)
def test_snap_now_keyword_date(dtm: date, expected_type: type[date], snaptime: str):
    # act
    result = snap(dtm, snaptime)

    # assert
    assert result == date(2024, 12, 30)
    assert type(result) is expected_type


@pytest.mark.parametrize(
    "dtm,expected_type",
    [(date(2024, 12, 30), date), (pendulum.date(2024, 12, 30), pendulum.Date)],
    ids=["date", "pendulum_date"],
)
def test_snap_range_now_keyword_date(dtm: date, expected_type: type[date]):
    # act
    result = snap_range(dtm, "-1d", "now")

    # assert
    assert result == (date(2024, 12, 29), date(2024, 12, 30))
    assert all(type(result_date) is expected_type for result_date in result)


@pytest.mark.parametrize(
    "dtm,snaptime,snap_dtm",
    [
        (pendulum.datetime(2024, 12, 30, 18, 52), "@w+6h", pendulum.datetime(2024, 12, 30, 6)),
        (datetime(2024, 12, 30, 18, 52), "@w+6h", datetime(2024, 12, 30, 6)),
        (
            datetime(2024, 12, 30, 18, 52, tzinfo=ZoneInfo("Europe/London")),
            "@h",
            datetime(2024, 12, 30, 18, tzinfo=ZoneInfo("Europe/London")),
        ),
    ],
    ids=["pendulum", "datetime_naive", "datetime_aware"],
)
def test_datetime_is_not_a_date(dtm: datetime, snaptime: str, snap_dtm: datetime):
    # act
    result = snap(dtm, snaptime)

    # assert
    assert result == snap_dtm
    assert type(result) is type(dtm)
    assert result.tzinfo is dtm.tzinfo
