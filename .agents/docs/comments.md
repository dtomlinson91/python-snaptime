<!-- cfb:begin slug=comments version=3 hash=7e812e6d -->
---
description: write or change a code comment in any file, config files included
---

## Comments

These rules apply to each comment that you write or change, in every file type, including config files such as the Makefile, `pyproject.toml` and the CI config. Do not rewrite other comments unless the user asks. A linter rule that the repo enforces wins over these rules. In all other cases, these rules override the comment style and the comment density of the surrounding code. A doc comment (a docstring, a Go doc comment or a JSDoc block) is not a comment in this sense.

A comment highlights important information. It does not document the code. Assume that the reader knows the language well and can read the code. Write a comment only when it states one of these:

- What a block does, when the code does not make this clear and it matters.
- A reason that the reader cannot get from the code: a constraint, a side effect, an external limit, or a workaround for a known bug.

If neither applies, write no comment.

A constraint is an external fact that the code must obey, for example an API limit or a required call order. A constraint is not the reason for a choice that we made, even when that reason reads like a constraint.

Allowed, because an external fact forces the code:

```python
# the listings API rejects pages larger than 100
PAGE_SIZE = 100
```

Not allowed, because each one explains a choice that we made:

```toml
# unpinned so that renovate can update it
requests = "*"
```

```python
# must use a dict, lookups have to be fast
index = {l.id: l for l in listings}
```

A comment must read the same whether a person or Claude wrote it. Do not:

- Narrate the code (`# loop through the listings`).
- Describe the change or the history of the code (`# now uses X`, `# fixed`, `# previously`).
- Refer to the conversation or the request (`# as requested`).
- Explain a design decision, an alternative, or why the code has this form and not another. Put that in the PR description or the ticket.
- Put a ticket ID (`DAT-1234`) in a comment, a log message or an error message.
- Leave commented-out code.

Format:

- Write one line, on its own line, directly above the code it refers to. Do not write multi-line comment blocks or comments at the end of a line of code.
- Write in lower case with no trailing full stop. Keep the case of identifiers, proper nouns and acronyms.
- Do not use emojis or em dashes.
- Tool directives (`# noqa`, `# type: ignore`, `//nolint`) stay where the tool needs them. They are exempt from these rules, and so are `TODO:` and `FIXME:` markers.
- File headers that the repo requires, such as a license header or a "generated file, do not edit" notice, are exempt.
<!-- cfb:end slug=comments -->
