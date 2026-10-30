# Changelog

All notable changes to this project are documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[1.0.0]: https://github.com/dtomlinson91/python-snaptime/compare/v0.1.1..v1.0.0
[0.1.0]: https://github.com/dtomlinson91/python-snaptime/releases/tag/v0.1.0

