<!-- cfb:begin slug=doc-comments version=3 hash=55bec2be -->
---
description: write or change a docstring, JSDoc, Go doc comment, rustdoc or Terraform description
---

## Docstrings and doc comments

These rules apply to each docstring and doc comment that you write or change. Doc comments include docstrings, JSDoc, Go doc comments, rustdoc and Terraform `description` fields. Do not rewrite others. A linter rule that the repo enforces wins over these rules.

- Follow the standard format of the language or the repo. A format that a tool parses wins over these rules, for example JSDoc tags, or a Go doc comment that starts with the name.
- The summary says what the function does, not how it does it.
- Do not put inline comments in a docstring or doc comment. Put the information in the summary or the description.
- Do not put design decisions, ticket IDs, emojis or em dashes in a docstring or doc comment.
- Text that renders for users follows its own convention, for example a docstring that becomes an OpenAPI description, or CLI help text. Do not rewrite it to match these rules.
<!-- cfb:end slug=doc-comments -->
