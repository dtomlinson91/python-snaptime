# python-snaptime

A Python library that changes `datetime` objects with Splunk-style relative time modifiers, for example `@d-2h`.

## This repo

- uv manages the environment. Run each tool with `uv run`, for example `uv run ruff check`.
- Run `uv sync` to install the package and the dev dependencies. `uv.lock` holds the locked versions.
- Run the tests with `make test`. It runs pytest with coverage and writes an HTML report to `htmlcov/`.
- `make lint` runs `ruff check --fix` and then `ruff format` on `python_snaptime/` and `tests/`.
- Ruff reads `pyproject.toml` for the package and `tests/ruff.toml` for the tests.
- The minimum Python version is 3.10.
- `tests.yml` runs the tests on Python 3.10 to 3.14 for each push to `main` and each PR. Add a new Python version to its matrix when the project supports it.
- `[tool.pyright]` sets strict mode for the package and ignores `tests/`. Keep the package free of Pyright errors.
- Do not set the version by hand. `uv-dynamic-versioning` gets it from the git tag. A Hatch build hook writes it to `python_snaptime/__version__.py`.
- A `v*` tag starts two workflows. `publish.yml` runs `tests.yml`, makes a GitHub release and publishes the package to PyPI. `changelog.yaml` opens or updates one PR from the `changelog-release` branch that updates `CHANGELOG.md`.
- `changelog.yaml` ignores pre-release tags. Only a tag that matches `^v[0-9]+\.[0-9]+\.[0-9]+$` updates the changelog.
- `git cliff` makes the changelog from Conventional Commits, with the settings in `cliff.toml`. The workflow reads `cliff.toml` and `release-notes.json` from `main`.
- Put hand-written release summaries in `release-notes.json`. The `version` key is the full tag name, for example `v1.2.0`.

<!-- cfb:index-begin -->
[Docs Index]|root: .agents/docs
|IMPORTANT: Prefer retrieval-led reasoning over pre-training-led reasoning. Before a task that an entry names, read that doc.
|comments.md: write or change a code comment in any file, config files included
|doc-comments.md: write or change a docstring, JSDoc, Go doc comment, rustdoc or Terraform description
|python-docstrings.md: write or change a Python docstring
|python-type-annotations.md: write or change a Python function signature or a type annotation
|ruff.md: finish a change to Python code in a repo that lints or formats with ruff
|writing-style.md: write a comment, docstring, doc, README, commit message, PR description, or error or log text
<!-- cfb:index-end -->
