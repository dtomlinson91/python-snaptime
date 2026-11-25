<!-- cfb:begin slug=python-type-annotations version=2 hash=740e1dc6 -->
---
description: write or change a Python function signature or a type annotation
---

## Python type annotations

- Annotate each argument and each return value.
- Use built-in types: `list[str]`, `dict[str, int]`, `type[Foo]`. Do not use `List`, `Dict` or `Type` from `typing`.
- Use `X | None`, not `Optional[X]`. Use `X | Y`, not `Union[X, Y]`.
- Import abstract types (`Callable`, `Iterable`, `Sequence`, `Mapping`) from `collections.abc`, not `typing`.
- Use the syntax of the minimum Python version in `pyproject.toml` (`requires-python`).
<!-- cfb:end slug=python-type-annotations -->
