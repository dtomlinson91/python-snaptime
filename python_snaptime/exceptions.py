"""Module defining exceptions for python-snaptime."""


class SnaptimeError(ValueError):
    """Error for an invalid snaptime string or an invalid snaptime operation.

    `SnaptimeError` is a subclass of `ValueError`, so `except ValueError` also catches it.
    """
