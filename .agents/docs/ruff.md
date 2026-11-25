<!-- cfb:begin slug=ruff version=2 hash=6d24453c -->
---
description: finish a change to Python code in a repo that lints or formats with ruff
---

## Lint and format with ruff

When you change Python code, run ruff at the end of the task, before you report the work as done. Ruff uses the settings in `pyproject.toml`.

1. Run `ruff check --fix` on the files that you changed. It also sorts the imports, if the settings select the `I` rules.
2. Run `ruff format` on the same files.
3. Run `ruff check` on the same files again. Fix each issue that it still reports by changing the code.

Run ruff from the repo's environment, for example `uv run ruff`, so that the version in the lock file runs.

An inline ignore (`# noqa`) is allowed only where the code breaks a rule on purpose, because of a deliberate design decision. Ask the user before you add one. Name the rule in it, for example `# noqa: PLR0913`. Do not change the ruff settings to make an issue go away. If you cannot fix an issue, tell the user.
<!-- cfb:end slug=ruff -->
