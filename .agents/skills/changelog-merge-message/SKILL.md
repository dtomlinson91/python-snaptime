---
name: changelog-merge-message
description: Writes the squash-merge commit message and extended description for a pull request, so that the changelog entry matches the style that the changelog already uses. Works in repos that use Conventional Commits and generate their changelog with git-cliff. Use this skill whenever the user asks for a commit message, a merge message, a squash message, a PR title, an "extended description", or a changelog entry for a branch or PR in such a repo, even if they do not say "changelog". Also use it before a PR is merged when the user wants to know how the change will show in the release notes.
---

# Changelog merge message

In the repos this skill is for, PRs are squash-merged into the default branch. The squash commit is the changelog entry. `git cliff` builds the changelog from these commits. The readers of the changelog are the users of the project, not the engineers who wrote the code.

The output of this skill is two pieces of text that the user pastes into the "Squash and merge" form of the Git host:

1. **Commit message**: the subject line. It is also the PR title.
2. **Extended description**: the commit body. It is also the PR body.

The PR body holds only the changelog text for users. Footer lines such as `BREAKING CHANGE:` or `Refs:` never go in the PR body or in the extended description. git-cliff copies them into the changelog. Put them in a comment on the PR.

The skill can also add one preprocessor to the git-cliff config. See [The PR number](#the-pr-number).

Do not commit, merge or push. The user does the merge.

## Step 1: Check the repo

1. Find the git-cliff config. git-cliff reads the first of these that exists:
   - `cliff.toml`, `.cliff.toml` or `.config/cliff.toml` at the repo root.
   - `[tool.git-cliff]` in `pyproject.toml`.
   - `[workspace.metadata.git-cliff]` or `[package.metadata.git-cliff]` in `Cargo.toml`.
2. If there is no config, tell the user. git-cliff then uses its built-in defaults, so continue with the Conventional Commits default types.
3. Find the changelog file. It is usually `CHANGELOG.md`. The `output` key in the config or the CI workflow that runs `git cliff` can name a different file.
4. Find the default branch: `git symbolic-ref --short refs/remotes/origin/HEAD`. Use `origin/main` if the command fails.

## Step 2: Read the change

1. Find the branch. Use the branch or PR that the user names. If they name none, use the current branch.
2. Read the commits: `git log --oneline <default>..<branch>`.
3. Read the diff: `git diff <default>...<branch>`. Exclude lock files and generated files, for example `':!*.lock' ':!package-lock.json'`. Read them separately only to find version changes.
4. If a PR exists, read its title and body. Use the CLI of the Git host, for example `gh pr view <branch>` for GitHub. The PR body often explains the reason for the change.

Identify what a user of the project will notice. Examples: a new endpoint, command or option, a new field, a changed default, a fix to a wrong result, better performance, a change to the docs.

## Step 3: Read the current style

Read the top 150 lines of the changelog. Then read these keys in the git-cliff config. Each one changes what the entry must look like:

| Key | What to check |
|---|---|
| `commit_parsers` | The prefixes that map to each group, and the prefixes with `skip = true`. git-cliff uses the first parser that matches, so read them in order. A parser on `body` can catch a commit before its prefix parser does. |
| `filter_unconventional` | If `true`, git-cliff drops a commit with no valid type prefix. Examples are `Merge branch 'x'` and `Update README`. |
| `filter_commits` | If `true`, git-cliff drops a commit that no parser matches. |
| `protect_breaking_commits` | If `true`, a breaking commit shows even when its parser has `skip = true`. |
| `split_commits` | If `true`, git-cliff parses each line of the message as a separate commit. git-cliff then drops each body line with no type prefix, so the body does not show. |
| `commit_preprocessors` | Rewrites that git-cliff applies to each message, for example to remove ticket IDs or to add links to PR numbers. |
| `body` template | Whether the template renders `commit.body`, `commit.scope` and `commit.breaking`, and how. Examples: a marker for breaking changes, an indent for each body line, `upper_first` on the subject. |

If the template does not render `commit.body`, the extended description does not show in the changelog. Keep it short, or leave it empty.

## Step 4: Choose the type

Use only a prefix that the parsers of this repo know. Choose the type from the effect on the user, not from the files that changed.

- New behaviour that a user can call or see: `feat`.
- Wrong behaviour that is now correct: `fix`.
- Faster, more stable or more scalable, with the same results: `perf`.
- A change to user-facing docs: `docs`, or `doc` if the parser matches `^doc` and the changelog uses `doc`.
- An internal change with no effect on users that the changelog shows: `refactor`, `build` or `test`, as the parsers allow.
- An internal change that must not show in the changelog: a prefix with `skip = true`, usually `chore` or `ci`.

A parser on the body can move a commit to a different group. For example, many configs send a commit with the word "security" in its body to a Security group. Use such a word only when the change matches that group.

Omit the scope unless the summary is unclear without it, or the changelog shows that the repo always uses scopes. If the template does not render `commit.scope`, the scope does not show in the changelog.

If the change breaks existing users, add `!` after the type, for example `fix!:`. Examples of breaking changes: a removed field, a renamed option, a changed response shape, a stricter validation rule. Tell the user that this release needs a major version (or a minor version before `1.0.0`).

## Step 5: Write the commit message

Format: `<type>[(scope)][!]: <Summary>`

- Match the capital letter at the start of the existing summaries. If the template applies `upper_first`, start with a capital letter anyway, because the Git host does not apply it.
- Use the imperative: "Add", "Fix", "Update", "Make".
- Put each code name in backticks. Code names include function, class, method, parameter, option, field, command, endpoint, module and file names. Literal values and syntax are code too, for example `@15m` or `str(Snaptime)`.
- The Git host and the changelog render the subject as Markdown. Without backticks, a name such as `__str__` shows as bold text, and the reader cannot see that it is code.
- If the user, a ticket or a plan gives the subject without backticks, add them. Do not change the other words.
- Keep it to one line, about 72 characters or fewer.
- Do not put a full stop at the end.
- Do not put a ticket ID in the summary, unless the existing entries do this.
- Do not add the PR number, for example ` (#1234)`. See [The PR number](#the-pr-number).

Examples:

```
feat: Add `--dry-run` option to the `sync` command
fix: Return a `404` when the user does not exist
perf: Cache the parsed config between requests
docs: Add the missing `limit` parameter to the API docs
feat!: Remove the deprecated `v1` endpoints
```

### The PR number

GitHub adds ` (#<number>)` to the end of the default squash title. The "Default commit message" setting of the repo chooses only the source of the title and the body. No setting removes the number.

By default, remove the number from the changelog with a preprocessor:

1. Read `commit_preprocessors` in the git-cliff config. If there is no git-cliff config, do not create one. Tell the user, and give only the last two options in step 5.
2. If an entry already matches the PR number, do not change the config. Such an entry can remove the number or add a link to the PR. Tell the user that the config already handles the number.
3. If not, add this entry to the end of `commit_preprocessors`. If the key does not exist, add it to the `git` table of the config.

   ```toml
   # GitHub adds the PR number to the squash title
   { pattern = '(?m) \(#[0-9]+\)$', replace = "" },
   ```

4. Tell the user that you changed the config, and name the file. Ask the user to say explicitly if they want to keep the change. Do not take silence, or an answer to a different question, as a yes.
5. Give the user these options:
   - **Keep the preprocessor.** git-cliff removes the number from the end of each line of the message. The git history keeps the number. This works for each merge, also when nobody removes the number by hand.
   - **Remove the number at each merge.** In the merge box, replace the whole title with the commit message. Or merge with the CLI: `gh pr merge <number> --squash --subject "<commit message>" --body "<extended description>"`. GitHub uses the subject exactly as given.
   - **Keep the number in the changelog.** Each entry then ends with ` (#<number>)`. A different preprocessor can change the number into a link to the PR.

If the user does not keep the preprocessor, remove the entry that you added. Leave the rest of the config as it was.

## Step 6: Write the extended description

The Git host fills the extended description with a list of every commit on the branch. Replace that list. A list of commits ("* fix tests", "* formatting") tells a user nothing, and git-cliff copies every line into the changelog.

Write for a user who reads the release notes. Match the length and tone of the entries already in the changelog:

- Use one or two plain sentences, or two to four short bullets. Do not use both a long paragraph and a long list.
- Write bullets in the format the changelog already uses. If there is no example, start each bullet with `- `, in lower case, with no full stop. Put one fact in each bullet.
- Put each code name in backticks, as in the subject.
- For a breaking change, list each old and new shape, for example "`count` is now `total`".

Leave the body empty if the subject says everything. A one-line fix does not need a body.

Do not put these in the body:

- Footer lines, for example `BREAKING CHANGE:`, `Refs:` or `Co-authored-by:`. Put them in a comment on the PR. To mark a breaking change, use `!` in the subject.
- Ticket IDs, PR numbers or branch names.
- Lock file changes, test changes, formatting, CI changes or other internal details.
- Names of internal files or functions, unless the user calls them.
- The phrase "this PR". The reader sees a release, not a PR.

Do not wrap lines by hand. One paragraph must be one line, or the changelog shows hard breaks.

Do not run `git cliff` to preview the entry.

## Output

Give only the two parts, in separate code blocks, so that the user can copy each one. If the change needs footer lines, give them in a third code block with the heading **PR comment**.

**Commit message**

```
<type>: <Summary>
```

**Extended description**

```
- <fact>
- <fact>
```

Do not add notes, previews or other text after the code blocks. Put any warning from Steps 1, 3, 4 or 5 before the code blocks, for example a missing config, a body that will not show, or a breaking change. Also put the change to the git-cliff config, the question about it and the options there.
