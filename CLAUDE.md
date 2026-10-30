# python-snaptime

<!-- cmb: managed by claude-md-builder (https://claude-md.membo.co.uk). Text between cmb:begin and cmb:end comes from the shared library. To change it, edit it here and ask Claude to push it. Text outside the blocks belongs to this repo. -->

A Python library that changes `datetime` objects with Splunk-style relative time modifiers, for example `@d-2h`.

## This repo

- uv manages the environment. Run each tool with `uv run`, for example `uv run ruff check`.
- Run `uv sync` to install the package and the dev dependencies. `uv.lock` holds the locked versions.
- Run the tests with `make test`. It runs pytest with coverage and writes an HTML report to `htmlcov/`.
- `make lint` runs isort, `ruff format` and pycln on `python_snaptime/` and `tests/`.
- Ruff reads `pyproject.toml` for the package and `tests/ruff.toml` for the tests.
- The minimum Python version is 3.10.
- `tests.yml` runs the tests on Python 3.10 to 3.14 for each push to `main` and each PR. Add a new Python version to its matrix when the project supports it.
- `[tool.pyright]` sets strict mode for the package and ignores `tests/`. Keep the package free of Pyright errors.
- Do not set the version by hand. `uv-dynamic-versioning` gets it from the git tag. A Hatch build hook writes it to `python_snaptime/__version__.py`.
- A `v*` tag starts two workflows. `publish.yml` runs `tests.yml`, makes a GitHub release and publishes the package to PyPI. `changelog.yaml` opens or updates one PR from the `changelog-release` branch that updates `CHANGELOG.md`.
- `changelog.yaml` ignores pre-release tags. Only a tag that matches `^v[0-9]+\.[0-9]+\.[0-9]+$` updates the changelog.
- `git cliff` makes the changelog from Conventional Commits, with the settings in `cliff.toml`. The workflow reads `cliff.toml` and `release-notes.json` from `main`.
- Put hand-written release summaries in `release-notes.json`. The `version` key is the full tag name, for example `v1.2.0`.

<!-- cmb:begin slug=writing-style version=1 hash=96b35fbc -->
## Writing style

Write the text that goes into the repo or to other people in Simplified Technical English (from ASD-STE100): code comments and docstrings, docs, READMEs, CLAUDE.md, skill and tool descriptions, commit messages, PR descriptions, and error and log messages. A reader must get the meaning at the first reading. Where a kind of text has its own format rules, such as the one-line, lower-case format of a code comment, those rules win. These rules do not apply to code, to quoted logs and output, or to text that someone else wrote.

- Use the active voice. Use the passive only when the actor is unknown or not important.
- Use plain verbs, not phrasal verbs: "start", not "spin up". "Remove", not "take off".
- Write one instruction in each sentence. Keep an instruction to 20 words or fewer, and a description to 25 words or fewer.
- Do not use semicolons. Make two sentences.
- Do not stack more than three nouns ("fuel pump valve").
- Keep the subject, the verb and the articles. Do not drop words to save space.
- Use a list for three or more steps or conditions. Number the steps when their order matters.
- Keep one topic in each paragraph, with six sentences or fewer.
- Use one word for one thing, and use it every time.
- Use the verb, not a noun made from it: "analyze the log", not "perform an analysis of the log".
- Keep each hedge: "may have failed" stays "may have failed". Do not add a claim that you cannot support.
- Do not use marketing words such as seamless, robust or powerful. Give the measurement instead.
- Use the simple tenses. Use the present perfect only when it adds information, for example "the job has completed".
<!-- cmb:end slug=writing-style -->

<!-- cmb:begin slug=comments version=1 hash=f84aca7a -->
## Comments

These rules apply to each comment that you write or change, in every file type, including config files such as the Makefile, `pyproject.toml` and the CI config. Do not rewrite other comments. A linter rule that the repo enforces wins over these rules. A doc comment (a docstring, a Go doc comment or a JSDoc block) is not a comment in this sense.

A comment highlights important information. It does not document the code. Write a comment only when it states one of these:

- What a block does, when the code does not make this clear and it matters.
- A reason that the reader cannot get from the code: a constraint, a side effect, an external limit, or a workaround for a known bug. A constraint is an external fact that the code must obey, for example an API limit.

Do not:

- Narrate the code (`# loop through the listings`).
- Describe the change or the history of the code (`# now uses X`, `# fixed`, `# previously`).
- Explain a design decision, an alternative, or why the code has this form and not another. Put that in the PR description.
- Put a ticket ID (`DAT-1234`) in a comment, a log message or an error message.
- Leave commented-out code.

Format:

- Write one line, on its own line, directly above the code it refers to. Do not write multi-line comment blocks or comments at the end of a line of code.
- Write in lower case with no trailing full stop. Keep the case of identifiers, proper nouns and acronyms.
- Do not use emojis or em dashes.
- Tool directives (`# noqa`, `# type: ignore`, `//nolint`) stay where the tool needs them. They are exempt from these rules, and so are `TODO:` and `FIXME:` markers.
<!-- cmb:end slug=comments -->

<!-- cmb:begin slug=doc-comments version=1 hash=914667f9 -->
## Docstrings and doc comments

These rules apply to each docstring and doc comment that you write or change. Do not rewrite others. A linter rule that the repo enforces wins over these rules.

- The summary says what the function does, not how it does it.
- Do not put design decisions, ticket IDs, emojis, em dashes or inline comments in a docstring or doc comment.
<!-- cmb:end slug=doc-comments -->

<!-- cmb:begin slug=python-docstrings version=1 hash=96355953 -->
## Python docstrings

- Use Google style. Give each `Args:` entry a type, for example `listing_ids (list[str]): ...`. Give `Returns:` and `Raises:` a type too. The types must match the annotations in the signature.
<!-- cmb:end slug=python-docstrings -->

<!-- cmb:begin slug=python-type-annotations version=1 hash=d8061f56 -->
## Python type annotations

- Annotate each argument and each return value.
- Use built-in types: `list[str]`, `dict[str, int]`, `type[Foo]`. Do not use `List`, `Dict` or `Type` from `typing`.
- Use `X | None`, not `Optional[X]`. Use `X | Y`, not `Union[X, Y]`.
- Import abstract types (`Callable`, `Iterable`, `Sequence`, `Mapping`) from `collections.abc`, not `typing`.
- Use the syntax of the minimum Python version in `pyproject.toml` (`requires-python`).
<!-- cmb:end slug=python-type-annotations -->

<!-- cmb:begin slug=ruff version=1 hash=8c7e726c -->
## Lint and format with ruff

When you change Python code, run ruff at the end of the task, before you report the work as done. Ruff uses the settings in `pyproject.toml`.

1. Run `ruff check --fix` on the files that you changed. It also sorts the imports, if the settings select the `I` rules.
2. Run `ruff format` on the same files.
3. Run `ruff check` on the same files again. Fix each issue that it still reports by changing the code.

Run ruff from the repo's environment, for example `uv run ruff`, so that the version in the lock file runs.

An inline ignore (`# noqa`) is allowed only where the code breaks a rule on purpose, because of a deliberate design decision. Ask the user before you add one. Name the rule in it, for example `# noqa: PLR0913`. Do not change the ruff settings to make an issue go away. If you cannot fix an issue, tell the user.
<!-- cmb:end slug=ruff -->
