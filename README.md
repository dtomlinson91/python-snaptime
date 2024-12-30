# python-snaptime

A modern replacement to the abandoned [zartstrom/snaptime](https://github.com/zartstrom/snaptime) package, `python-snaptime` will transform `datetime` objects using relative time modifiers.

- Use snaptime strings to get relative dates/times for a given datetime.
- Timezone aware.
- Effortlessly handles daylight savings using [pendulum](https://github.com/python-pendulum/pendulum).
- Can snap to seconds, minutes, hours, days, weeks, months, quarters or years.
- Can add/subtract milliseconds, seconds, minutes, hours, days, weeks, months, quarters or years.

This package is inspired by Splunk's [relative time modifiers](http://docs.splunk.com/Documentation/Splunk/latest/SearchReference/SearchTimeModifiers#How_to_specify_relative_time_modifiers).

## Examples

### Timezones

Using `pendulum` timezones are handled easily.

```python
>>> import pendulum
>>> from python_snaptime import snap
>>> snap(pendulum.datetime(2024, 12, 30, 18, 0, 0), "@d-12h")
DateTime(2024, 12, 29, 12, 0, 0, tzinfo=Timezone('UTC'))
```

```python
>>> import pendulum
>>> from python_snaptime import snap
>>> snap(pendulum.datetime(2024, 12, 30, 18, 0, 0, tz=pendulum.timezone("Europe/London")), "@d-12h")
DateTime(2024, 12, 29, 12, 0, 0, tzinfo=Timezone('Europe/London'))
```

### DST

`pendulum` makes working around DST easy

```python
>>> import pendulum
>>> from python_snaptime import snap
>>> snap(pendulum.datetime(2024, 10, 27, 1, 59, 59, tz="Europe/London", fold=0), "+1s")
DateTime(2024, 10, 27, 1, 0, 0, tzinfo=Timezone('Europe/London'))  # pre-transition
```

```python
>>> import pendulum
>>> from python_snaptime import snap
>>> snap(pendulum.datetime(2024, 10, 27, 1, 59, 59, tz="Europe/London", fold=1), "+1s")
DateTime(2024, 10, 27, 2, 0, 0, tzinfo=Timezone('Europe/London'))  # post-transition (default)
```

### datetime

Don't care about timezones/want to use builtin `datetime.datetime`?

```python
>>> from datetime import datetime
>>> from python_snaptime import snap
>>> snap(datetime(2024, 12, 30, 18, 0, 0), "@d-12h")
datetime.datetime(2024, 12, 29, 12, 0)
```

Can also work with builtin timezone aware datetimes

```python
>>> import pytz
>>> from datetime import datetime
>>> from python_snaptime import snap
>>> snap(datetime(2024, 12, 30, 18, 0, 0, tzinfo=pytz.timezone("Europe/London")), "@d-12h")
datetime.datetime(2024, 12, 29, 12, 0, tzinfo=Timezone('Europe/London'))
```

If using Python >=3.9 can use builtin `ZoneInfo`

```python
>>> from datetime import datetime
>>> from zoneinfo import ZoneInfo
>>> from python_snaptime import snap
>>> snap(datetime(2024, 12, 30, 18, 0, 0, tzinfo=ZoneInfo("Europe/London")), "@d-12h")
datetime.datetime(2024, 12, 29, 12, 0, tzinfo=Timezone('Europe/London'))
```
