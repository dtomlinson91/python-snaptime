import pendulum
from python_snaptime import snap


def main():
    snaptimes = [
        "@d",
        "@h-2h",
        "@m+30m",
        "@s-500ms",
        "@w@d+1000us",
        "@mon-1w+250ms",
        "@q+1mon-750us",
        "@y@q+1500ms",
        "@d@h-6h+3s",
        "@h@m+45m-2s",
        "@w-2d@d+100ms",
        "@mon+1w@w-250us",
        "@q-1mon@mon+1s",
        "@y+3mon@q-750ms",
        "@d@h@m-30m+500us",
        "@h-4h@m+15m-1s",
        "@w+3d@d-12h+350ms",
        "@mon-2w@w+4d-1250us",
        "@q+2mon@mon-1w+2s",
        "@y-1q@q+1mon-900ms",
        "@d+1d@h-6h@m+1500us",
        "@h@m-45m@s+30s",
        "@w@d-1d@h+12h-750ms",
        "@mon@w+1w@d-3d+1s",
        "@q@mon-2mon@w+1w-500us",
        "@y@q+1q@mon-2mon+3s",
        "@d@h-12h@m+30m@s-1750ms",
        "@h-3h@m+45m@s-15s",
        "@w+2d@d-1d@h+6h+2000us",
        "@mon-3w@w+1w@d-2d-1s",
        "@q+1mon@mon-2w@w+3d+850ms",
        "@y-2q@q+2mon@mon-3w-1500us",
        "@d+2d@h-18h@m+45m@s+4s",
        "@h@m-50m@s+45s@m+5m",
        "@w@d-3d@h+18h@m-30m+750ms",
        "@mon@w+2w@d-4d@h+12h-2s",
        "@q@mon-1mon@w+2w@d-1d+1250us",
        "@y@q+2q@mon-3mon@w+1w-3s",
        "@d@h@m@s-45s@m+15m+500ms",
        "@h-5h@m+50m@s-40s@m+10m-750us",
        "@w+3d@d-2d@h+14h@m-45m+1s",
        "@mon-2w@w+10d@d-5d@h+8h-1000ms",
        "@q+2mon@mon-6w@w+3w@d-2d+2s",
        "@y-1y@q+2q@mon-4mon@w+2w-1500us",
        "@d+3d@h-36h@m+90m@s-120s+250ms",
        "@h@m@s-55s@m+25m@h-1h@m+35m-500us",
        "@w@d@h-30h@m+150m@s-300s@m+60m+2000ms",
        "@mon@w@d-10d@h+120h@m-360m@s+1800s-750us",
        "@q@mon@w-3w@d+15d@h-180h@m+600m+4s",
        "@y-2y@q+3q@mon-9mon@w+26w@d-150d@h+1800h@m-54000m@s+3240000s-1500ms+2000us",
    ]

    dtm = pendulum.datetime(2024, 12, 30, 13, 1, 10, 999999, tz=pendulum.timezone("America/New_York"))
    for snaptime in snaptimes:
        result = snap(dtm, snaptime)
        print(
            f"{result.year},{result.month},{result.day},{result.hour},{result.minute},{result.second},{result.microsecond}"
        )


if __name__ == "__main__":
    main()
