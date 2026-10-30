import re
import time
from datetime import date, datetime, timedelta, timezone, tzinfo
from zoneinfo import ZoneInfo

import pendulum
import pytest
from python_snaptime import snap, snap_range


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
        dtm = date(2024, 12, 30)

        # arrange/act
        with pytest.raises(
            TypeError, match=re.escape("Invalid datetime type. Must be pendulum.DateTime or datetime.datetime.")
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
            ValueError, match=re.escape("The range from '@d' to '@d' is empty. An inclusive range must not be empty.")
        ):
            snap_range(dtm, "@d", "@d", inclusive=True)

    @pytest.mark.parametrize("dtm", [pendulum.datetime(2024, 12, 30, 18), datetime(2024, 12, 30, 18)])
    @pytest.mark.parametrize("inclusive", [False, True])
    def test_snap_range_reversed(self, dtm: datetime, inclusive: bool):
        # act/assert
        with pytest.raises(ValueError, match=re.escape("The start of the range ('@d') is after the end ('-1d@d').")):
            snap_range(dtm, "@d", "-1d@d", inclusive=inclusive)

    def test_snap_range_invalid_datetime(self):
        # act/assert
        with pytest.raises(TypeError, match=re.escape("Invalid datetime type.")):
            snap_range(date(2024, 12, 30), "-1d@d", "@d")
