# python-snaptime

![PyPI - Version](https://img.shields.io/pypi/v/python-snaptime?style=flat-square)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/python-snaptime)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/dtomlinson91/python-snaptime/codacy.yml?style=flat-square)
![Codacy coverage](https://img.shields.io/codacy/coverage/d252742da60f4d90b72aa7d7de1a7a2f?style=flat-square)
![Codacy grade](https://img.shields.io/codacy/grade/d252742da60f4d90b72aa7d7de1a7a2f?style=flat-square)


Inspired by Splunk's [relative time modifiers](http://docs.splunk.com/Documentation/Splunk/latest/SearchReference/SearchTimeModifiers#How_to_specify_relative_time_modifiers), `python-snaptime` will transform `datetime` objects using relative time modifiers.

For example, `@d-2h` will give you two hours ago from the start of the day.

- Use snaptime strings to get relative dates/times for a given datetime.
- Use [pendulum](https://github.com/python-pendulum/pendulum) or builtin [datetime](https://docs.python.org/3/library/datetime.html#datetime-objects).
- Timezone aware.
- Handles daylight savings with `fold`.
- Can snap backwards in time to the nearest second, minute, hour, day, week, month, quarter or year.
- Can add/subtract microseconds, milliseconds, seconds, minutes, hours, days, weeks, months, quarters or years.
- Chain snaps together as needed e.g `@d-12h+10m@h`.
- Use either a snaptime string, or use Python to define snaptimes ([see advanced example](#advanced)).
- Fully type annotated for IDE completion.

> [!NOTE]
> This package was created as a more up to date replacement for [zartstrom/snaptime](https://github.com/zartstrom/snaptime), which is long since abandoned.

## Snaptime strings

| Unit          | Strings                                   | Supports Snapping? | Supports Delta? |
| :------------ | :---------------------------------------- | :----------------: | :-------------: |
| `MICROSECOND` | `us`, `microsecond`, `microseconds`       |         ❌         |       ✅        |
| `MILLISECOND` | `ms`, `millisecond`, `milliseconds`       |         ❌         |       ✅        |
| `SECOND`      | `s`, `sec`, `secs`, `second`, `seconds`   |         ✅         |       ✅        |
| `MINUTE`      | `m`, `min`, `mins`, `minute`, `minutes`   |         ✅         |       ✅        |
| `HOUR`        | `h`, `hr`, `hrs`, `hour`, `hours`         |         ✅         |       ✅        |
| `DAY`         | `d`, `day`, `days`                        |         ✅         |       ✅        |
| `WEEK`        | `w`, `week`, `weeks`                      |         ✅         |       ✅        |
| `MONTH`       | `mon`, `month`, `months`                  |         ✅         |       ✅        |
| `QUARTER`     | `q`, `qtr`, `qtrs`, `quarter`, `quarters` |         ✅         |       ✅        |
| `YEAR`        | `y`, `yr`, `yrs`, `year`, `years`         |         ✅         |       ✅        |

A snaptime string can contain only `@`, `+`, `-`, digits and the unit strings in the table. Any other character, including a space, raises a `SnaptimeError`.

> [!NOTE]
> By default, `@w` snaps to the start of the week on Monday. In Splunk, `@w` snaps to Sunday. To use a different first day of the week, set `week_start`, for example `snap(dtm, "@w", week_start=Weekday.SUNDAY)`.

`@` can take a multiple of `s`, `m` or `h`. For example, `@15m` snaps to 00, 15, 30 or 45 minutes past the hour. The multiple must divide 60 for `s` and `m`, and 24 for `h`. `@1m` is the same as `@m`. Splunk does not support this syntax.

## Examples

### Timezones

Using `pendulum` timezones are handled easily.

```python
>>> import pendulum
>>> from python_snaptime import snap

>>> dtm = pendulum.datetime(2024, 12, 30, 18, 0, 0)
>>> snap(dtm, "@d-12h")
DateTime(2024, 12, 29, 12, 0, 0, tzinfo=Timezone('UTC'))
```

```python
>>> import pendulum
>>> from python_snaptime import snap

>>> dtm = pendulum.datetime(2024, 12, 30, 18, 0, 0, tz=pendulum.timezone("Europe/London"))
>>> snap(dtm, "@d-12h")
DateTime(2024, 12, 29, 12, 0, 0, tzinfo=Timezone('Europe/London'))
```

### datetime

Don't care about timezones/want to use builtin `datetime.datetime`?

```python
>>> from datetime import datetime
>>> from python_snaptime import snap

>>> dtm = datetime(2024, 12, 30, 18, 0, 0)
>>> snap(dtm, "@d-12h")
datetime.datetime(2024, 12, 29, 12, 0)
```

Can also work with builtin timezone aware datetimes

```python
>>> from datetime import datetime
>>> from zoneinfo import ZoneInfo
>>> from python_snaptime import snap

>>> dtm = datetime(2024, 12, 30, 18, 0, 0, tzinfo=ZoneInfo("Europe/London"))
>>> snap(dtm, "@d-12h")
datetime.datetime(2024, 12, 29, 12, 0, tzinfo=Timezone('Europe/London'))
```

### DST

Use `fold` to work with DST.

```python
>>> import pendulum
>>> from python_snaptime import snap

>>> dtm = pendulum.datetime(2024, 10, 27, 1, 59, 59, tz="Europe/London", fold=0)
>>> snap(dtm, "+1s")
DateTime(2024, 10, 27, 1, 0, 0, tzinfo=Timezone('Europe/London'))  # pre-transition
```

```python
>>> import pendulum
>>> from python_snaptime import snap

>>> dtm = pendulum.datetime(2024, 10, 27, 1, 59, 59, tz="Europe/London", fold=1)
>>> snap(dtm, "+1s")
DateTime(2024, 10, 27, 2, 0, 0, tzinfo=Timezone('Europe/London'))  # post-transition (default)
```

## Installation

### pypi

```sh
# using uv
uv add python-snaptime

# using poetry
poetry add python-snaptime

# using pip
pip install python-snaptime
```

## Usage

```python
import pendulum
from python_snaptime import (
    SnaptimeError, Weekday, apply, compile, is_valid, parse, snap, snap_now, snap_range, to_string,
)

now = pendulum.datetime(2024, 12, 30, 18, 52)  # Monday

snap(now, "@d")                             # 2024-12-30 00:00, start of today
snap(now, "@d-2h+10m")                      # 2024-12-29 22:10
snap(now, "@15m")                           # 2024-12-30 18:45, 15-minute bucket
snap(now, "@w", week_start=Weekday.SUNDAY)  # 2024-12-29 00:00
snap_now("@h", tz="Europe/London")          # start of the current hour in London

snap_range(now, "-1d@d", "@d")                  # (2024-12-29 00:00, 2024-12-30 00:00)
snap_range(now, "-1d@d", "@d", inclusive=True)  # (2024-12-29 00:00, 2024-12-29 23:59:59.999999)

ops = parse("@d-2h")    # parse once
apply(now, ops)         # 2024-12-29 22:00, apply many times
to_string(ops)          # "@d-2h"

yesterday = compile("-1d@d")
yesterday.apply(now)    # 2024-12-29 00:00

is_valid("@d-2h")       # True
is_valid("@ms")         # False
snap(now, "@ms")        # raises SnaptimeError, a subclass of ValueError
```

### Advanced

You can programmatically calculate snaptimes without a snaptime string, e.g the equivalent of `@d-2h+10m` is:

```python
import pendulum

from python_snaptime import Action, Snaptime, Unit, apply

operations = [
    Snaptime(action=Action.SNAP, unit=Unit.DAY),
    Snaptime(action=Action.SUB, unit=Unit.HOUR, time_int=2),
    Snaptime(action=Action.ADD, unit=Unit.MINUTE, time_int=10),
]
apply(pendulum.now(), operations)  # `@d-2h+10m`
```
