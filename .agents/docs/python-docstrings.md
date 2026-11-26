<!-- cfb:begin slug=python-docstrings version=4 hash=8f5d7760 -->
---
description: write or change a Python docstring
---

## Python docstrings

These rules apply to each docstring that you write or change. Do not rewrite other docstrings. A linter rule that the repo enforces wins over these rules.

A FastAPI route handler has its own docstring rules: read python-fastapi.md first.

- Follow the standard format of the repo. A format that a tool parses wins over these rules.
- The summary says what the function does, not how it does it.
- Write for the caller. Give what a caller needs to write a correct call: what to pass, what comes back, what can fail. Do not explain the implementation, how other code calls this function, or the project facts that made a parameter necessary. Describe a parameter by what the caller passes and how the result changes.
- Do not put inline comments in a docstring. Put the information in the summary or the description.
- Do not put design decisions, ticket IDs, emojis or em dashes in a docstring.
- Text that renders for users follows its own convention, for example CLI help text. Do not rewrite it to match these rules.

Format:

- Use Google style. Give each `Args:` entry a type, for example `listing_ids (list[str]): ...`. Give `Returns:` and `Raises:` a type too. The types must match the annotations in the signature.

Good:

```python
def fetch_listings(listing_ids: list[str], timeout: float | None = None) -> list[Listing]:
    """Fetch the listings with the given IDs, in the order of the IDs.

    Args:
        listing_ids (list[str]): The IDs of the listings to fetch.
        timeout (float | None): The timeout of each request in seconds, or None for no timeout.

    Returns:
        list[Listing]: The listings, one for each ID that exists.

    Raises:
        ListingsAPIError: If the listings API returns an error.
    """
```

Bad, because it explains the callers and the internals, and its `Args:` entry has no type:

```python
def fetch_listings(listing_ids: list[str], timeout: float | None = None) -> list[Listing]:
    """Fetch the listings.

    The sync job passes the IDs newest first, so this function sorts them
    before it sends one request for each batch of 100.

    Args:
        listing_ids: The IDs.
    """
```

Bad, because it explains how other code calls the method and the project facts behind the parameter:

```python
def totals(self, swapped: bool = False) -> Totals:
    """Return the totals of the report.

    The export job builds reports with the debit and credit columns
    swapped, so with swapped=True this method swaps them back.
    """
```

Good, because it says what the caller passes and how the result changes:

```python
def totals(self, swapped: bool = False) -> Totals:
    """Return the debit, credit and balance totals of the report.

    Args:
        swapped (bool): True if the report has its debit and credit columns
            in the opposite order. The totals are the same either way.

    Returns:
        Totals: The debit, credit and balance totals.
    """
```
<!-- cfb:end slug=python-docstrings -->
