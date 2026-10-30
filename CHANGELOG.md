# Changelog

All notable changes to this project are documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-10-30

### Release Summary

A minor release. It adds a public API to parse, apply, compile and check snaptime strings, and it removes the pydantic dependency. pendulum is now the only runtime dependency.

### 🎯 Highlights

- `parse` and `apply` parse a snaptime string once and apply it to many datetimes. `compile` returns a reusable object, like `re.compile`

- `snap_range` returns a start and an end datetime from two snaptime strings. `snap_now` snaps the current time

- `@15m` snaps to a multiple of a unit. `week_start` sets the first day of the week for `@w`

- Invalid snaptime strings raise `SnaptimeError`, a subclass of `ValueError`. `is_valid` checks a string without an exception

### 🚨 Migration Notes

- This release has a breaking change in a minor version. The risk to users is low

- `Snaptime` is now a frozen dataclass, not a pydantic model. `model_dump`, `model_validate` and attribute assignment no longer work

- Invalid input raises `SnaptimeError`, not `pydantic.ValidationError`. Code that catches `ValueError` keeps working

- pydantic is no longer installed with python-snaptime. If your code imports pydantic, add it to your own dependencies

---

### ✨ Features

- Export the advanced API from the `python_snaptime` package

    - `handle_timesnapping` can now be imported with `from python_snaptime import handle_timesnapping`
    - the `Snaptime`, `Action` and `Unit` models can now be imported from `python_snaptime`

- Snap to a multiple of a unit, for example `@15m`
- Add `to_string` and `str(Snaptime)` to convert snaptimes back to a string

    - `Snaptime` now raises a `ValueError` for a negative `time_int`

- Add `parse` and `apply` to parse a snaptime string once and apply it many times
- Add `snap_range` to get a start and an end datetime from two snaptime strings
- Add `snap_now` to snap the current time
- Add a `week_start` option to set the first day of the week for `@w`
- Add `compile` to make a reusable snaptime object
- Raise `SnaptimeError` for invalid snaptime strings
- Add `is_valid` to check a snaptime string

### 📘 Documentation

- Add uv installation instructions and update import examples
- Add v1.1.0 release notes

### 🛠 Refactor

- 💥 **BREAKING CHANGE**: Remove the pydantic dependency

    - `Snaptime` is now a frozen dataclass, not a pydantic model.
    `model_dump`, `model_validate` and attribute assignment no longer work
    - invalid input raises `ValueError`, not `pydantic.ValidationError`.


## [1.0.0] - 2026-10-30

### Release Summary

A major release. It removes support for Python 3.9, keeps the timezone of aware datetimes, and rejects snaptime strings that contain unknown characters.

### 🎯 Highlights

- Support for pendulum 2. The package now accepts `pendulum>=2,<4`

- `snap` now returns an aware `datetime.datetime` with the same `tzinfo` as the input

### 🚨 Migration Notes

- The minimum Python version is now 3.10. Python 3.9 is not supported

- The minimum `pydantic` version is now 2.13.5

- A snaptime string can contain only `@`, `+`, `-`, digits and unit strings. Any other character, including a space, raises a `ValueError`. For example, change `@d -2h` to `@d-2h`

---

### 🐛 Bug Fixes

- Add support for pendulum v2
- 💥 **BREAKING CHANGE**: Keep the `tzinfo` of aware datetimes and reject unknown characters

    - `snap` now returns an aware `datetime.datetime` with the same `tzinfo`
    as the input
    - a snaptime string can contain only `@`, `+`, `-`, digits and unit
    strings. Any other character, including a space, raises a `ValueError`
    - the README now states that `@w` snaps to Monday, not to Sunday as in
    Splunk


### 🧪 Testing

- Fix tests

## [0.1.0] - 2025-01-01


### ✨ Features

- Initial release

[1.1.0]: https://github.com/dtomlinson91/python-snaptime/compare/v1.0.0..v1.1.0
[1.0.0]: https://github.com/dtomlinson91/python-snaptime/compare/v0.1.1..v1.0.0
[0.1.0]: https://github.com/dtomlinson91/python-snaptime/releases/tag/v0.1.0

