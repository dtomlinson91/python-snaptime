---
name: initialise-changelog
description: Sets up a git-cliff changelog for a GitHub repo that uses Conventional Commits. Each stable release tag regenerates CHANGELOG.md and opens or updates one rolling pull request, through peter-evans/create-pull-request. Pre-release tags such as v1.0.0-dev and v1.0.0.dev0 are excluded. Detects the repo state and asks the user what they want. Writes cliff.toml, the workflow and an optional release-notes.json. Then guides the user through the GitHub settings, the token and the permissions. Use this skill when the user asks to set up, add, initialise or automate a changelog, release notes or git-cliff in a repo, or asks for a changelog PR on each tag, even if they do not say "git-cliff".
argument-hint: "[repo path, or blank for the current repo]"
---

# Initialise changelog

Set up this pipeline in a GitHub repo:

1. A maintainer pushes a stable tag, for example `v1.4.0`.
2. The `Changelog` workflow runs git-cliff on the full history up to that tag.
3. The workflow puts the new `CHANGELOG.md` on the rolling branch `changelog-release`, and opens or updates one PR into the default branch.
4. A maintainer merges the PR when they want the changelog on the default branch.

The pipeline assumes that the squash commit of each PR is a conventional commit. This skill does not check PR titles.

## Rules

- Do not commit, stage or push. Leave every change in the working tree. Use `mv`, not `git mv`.
- Do not change GitHub settings, variables or secrets without the user's explicit approval of that command. Read-only `gh api` calls are allowed.
- Do not delete existing workflows or files. Report them and let the user decide.

## Files

| File | Purpose |
|---|---|
| [templates/cliff.toml](templates/cliff.toml) | git-cliff config: groups, revert handling, removal of the GitHub PR number, stable-only `tag_pattern`, the release-notes block |
| [templates/changelog.yaml](templates/changelog.yaml) | The workflow. Copy it to `.github/workflows/changelog.yaml` |
| [scripts/detect.sh](scripts/detect.sh) | Read-only detection. Prints JSON |

## Step 1: Detect

Run `scripts/detect.sh [repo-dir]`. It reports:

- `repo`: the GitHub slug and the default branch. If `github` is `false`, stop. The workflow and the PR action work on GitHub only.
- `tags`: the counts of each tag shape, and the oldest and latest stable tags.
- `commits`: how many of the last 100 first-parent commits git-cliff will keep (conventional or `Revert "`).
- `existing`: any git-cliff config, the top of `CHANGELOG.md`, `release-notes.json`, and workflows that already run git-cliff or create PRs.
- `github`: the merge settings, the Actions workflow permissions for the repo and the org, the rules on the default branch, and whether the `CHANGELOG_APP_CLIENT_ID` variable exists. `null` means that the user's token cannot read that setting.

Give the user a short summary of the findings before you ask anything. Say what each finding means. For example: "kraken-v2 has 80 `-dev` tags. The workflow ignores them, and their commits go into the next stable release."

## Step 2: Ask

Use AskUserQuestion. Ask only what Step 1 cannot answer. Put the recommended option first.

**Round 1, always:**

1. **Tags.** "Which tag format marks a release?" Options: `v1.2.3` and `1.2.3`. Recommend the format that the detected stable tags use. In the question, say that every pre-release form is excluded: `-dev`, `.devN`, `-rc.N`, `rcN`, `aN`, `bN`.
2. **Types.** "Which commit types show in the changelog?"
   - All except `style`, `ci` and `chore` *(recommended)*: feat, fix, perf, revert, docs, refactor, test, build.
   - User-facing only: feat, fix, perf, revert, docs.
3. **Headings.** "Emoji in the group headings?" Options: emoji (`✨ Features`) or plain (`Features`).
4. **Release notes.** "Create `release-notes.json` for hand-written summaries?" Options: yes (recommended) or not now. Say that the workflow uses the file when it exists, so the user can add it later.

**Round 2, only the questions that apply:**

5. **Squash settings**, if `merge_settings` is not squash-only with title `PR_TITLE`. "Set the merge settings so that each PR becomes one conventional commit?"
   - Squash only, title from the PR title, body from the PR description *(recommended)*.
   - Squash only, title from the PR title, empty body.
   - Leave the settings unchanged.
6. **Existing config**, if `existing.cliff_config` is set. "Replace the existing git-cliff config?" Options: replace, or keep it and add only the workflow. If the user keeps it, check its `tag_pattern` against Step 3. A `skip_tags` value that matches dev tags drops their commits.
7. **Existing changelog**, if `CHANGELOG.md` exists and git-cliff did not generate it. Look for the header and the `## [x.y.z] - date` lines. "The first PR replaces `CHANGELOG.md`. Keep the old file?" Options: keep it as `CHANGELOG-legacy.md` and link it from the header, or replace it.
8. **Old history**, if there are stable tags and less than about 80% of the sampled commits are conventional. "Releases from before Conventional Commits will show few or no entries. Include them?" Options: include all releases, or leave out releases older than a version the user names. For the second option, set `skip_tags` to a regex for those tags, for example `'^v0\.'`.

Do not ask about the token. The workflow uses `GITHUB_TOKEN` and changes to a GitHub App token when the App variable exists. Step 5 covers this.

## Step 3: Write the files

1. Check the versions. The templates pin known-good versions. Read the latest versions with `gh api repos/<owner>/<repo>/releases/latest --jq .tag_name` for `orhun/git-cliff`, `actions/checkout`, `actions/create-github-app-token`, `taiki-e/install-action` and `peter-evans/create-pull-request`. If a newer major version exists, read its release notes before you use it. A major version can rename inputs.
2. Copy `templates/cliff.toml` to `cliff.toml`. Copy `templates/changelog.yaml` to `.github/workflows/changelog.yaml`.
3. Replace the placeholders in both files:

   | Placeholder | `v1.2.3` tags | `1.2.3` tags |
   |---|---|---|
   | `@@TAG_REGEX@@` | `^v[0-9]+\.[0-9]+\.[0-9]+$` | `^[0-9]+\.[0-9]+\.[0-9]+$` |
   | `@@TAG_GLOB@@` | `v*` | `[0-9]*` |
   | `@@EXAMPLE_TAG@@` | `v1.2.0` | `1.2.0` |
   | `@@REPO_URL@@` | `https://github.com/<slug>` | `https://github.com/<slug>` |

   The regex is in single quotes in both files, so do not escape the backslashes. The workflow regex and `tag_pattern` must be the same.

4. Apply the answers:
   - Types: add `skip = true` to the parser of each hidden type. Keep its `group`, because a breaking commit of a skipped type still shows under that group.
   - Plain headings: remove the emoji from each `group`, from the `🎯` and `🚨` headings, and from the `💥` marker.
   - Old history: set `skip_tags`.
   - Legacy changelog: run `mv CHANGELOG.md CHANGELOG-legacy.md`. Add a line to the `header` template, for example `For releases before 2.0.0, see [CHANGELOG-legacy.md](CHANGELOG-legacy.md).`
5. If the user wants release notes, write `release-notes.json` with the content `[]`. Show them the shape of an entry:

   ```json
   [
     {
       "version": "v1.4.0",
       "release_notes": {
         "summary": "A minor release that adds bulk export.",
         "highlights": ["Export up to 10,000 rows in one request"],
         "migration_notes": ["`limit` now defaults to 100"]
       }
     }
   ]
   ```

   `version` is the full tag name. Lists are optional, and the template adds the `- ` before each item. The workflow reads the file from the default branch, so notes added after the tag still appear at the next run.

## Step 4: Check

1. If git-cliff is installed, run `git cliff --config cliff.toml | head -80`. Do not write `CHANGELOG.md`, because the first PR does that.
   - `git cliff --config cliff.toml | grep '^## \['` must list only stable versions.
   - If the output has many empty releases, tell the user and offer the old-history option from Step 2.
   - Without the `[remote.github]` block, git-cliff makes no GitHub API calls and needs no token.
   - If git-cliff is not installed, tell the user to run `brew install git-cliff` or `cargo install git-cliff`. Do not install it yourself.
2. If `release-notes.json` exists, run `jq empty release-notes.json`.
3. If actionlint is installed, run it on the workflow. actionlint 1.7.12 has data for `create-github-app-token` v3.0.0 only. It reports that `client-id` is unknown and that `app-id` is required. Ignore those two errors: `v3` points to v3.3.0, which accepts `client-id` and deprecates `app-id`.

## Step 5: Guide the setup

Give the user only the items that apply, in this order. For each settings change, show the command and the reason. Ask before you run it. Each command needs repo admin rights unless the item says otherwise.

**1. Allow Actions to create PRs.** This is required when the workflow uses `GITHUB_TOKEN`. Skip it if the user sets up the App (item 4).

```sh
gh api -X PUT repos/<slug>/actions/permissions/workflow \
  -f default_workflow_permissions=read -F can_approve_pull_request_reviews=true
```

The workflow's own `permissions:` block grants `contents: write` and `pull-requests: write`, so the default stays `read`. If the org disables this setting, the repo cannot enable it. An org owner must allow it at org Settings → Actions → General → Workflow permissions. `actions_org: null` from Step 1 means that the user could not read the org setting.

**2. Squash settings**, if the user chose them in Step 2:

```sh
gh api -X PATCH repos/<slug> -F allow_squash_merge=true -F allow_merge_commit=false \
  -F allow_rebase_merge=false -f squash_merge_commit_title=PR_TITLE -f squash_merge_commit_message=PR_BODY
```

Use `BLANK` instead of `PR_BODY` for an empty body. The reasons:
- git-cliff reads only the commits on the default branch.
- With `COMMIT_OR_PR_TITLE`, a PR with one commit uses the commit message, not the PR title.
- A merge commit is not conventional, so git-cliff drops it.
- A rebase merge puts every branch commit into the changelog.

**3. Required checks.** If `default_branch_rules` contains `required_status_checks`, or the branch has classic protection with required checks, a PR from `GITHUB_TOKEN` cannot merge. GitHub does not start workflows for events that `GITHUB_TOKEN` causes, so the checks never run. Give the user two options:
- Set up the App (item 4). This is the permanent fix.
- Before each merge, close and reopen the PR. The reopen comes from a person, so the checks run.

**4. Optional GitHub App.** A PR from an App token starts the other workflows. The workflow needs no change.

1. Create the App at org Settings → Developer settings → GitHub Apps → New GitHub App. For a personal repo, use personal Settings. Clear "Active" under Webhook.
2. Set the repository permissions: Contents "Read and write", Pull requests "Read and write". GitHub sets Metadata to "Read-only".
3. Under "Where can this GitHub App be installed?", choose "Only on this account" for one org. Choose "Any account" to use one App in several orgs.
4. Generate a private key. The browser downloads a `.pem` file.
5. Install the App on the repo: App settings → Install App → Only select repositories.
6. Store the Client ID (from the App's General page) and the key. Run these commands, or let the user run them, so that the key does not pass through the conversation:

   ```sh
   gh variable set CHANGELOG_APP_CLIENT_ID --repo <slug> --body <client-id>
   gh secret set CHANGELOG_APP_PRIVATE_KEY --repo <slug> < path/to/key.pem
   ```

   For several repos in one org, use `--org <org> --repos <repo1>,<repo2>` instead of `--repo`. This needs org admin rights.
7. For another org: install the same App there and store the variable and the secret in that org. A fine-grained PAT is not a good alternative. It covers one org only, it expires, and it belongs to one person.

**5. Rules on the default branch.** `sign-commits: true` makes GitHub sign the commit, so a `required_signatures` rule passes. If a ruleset limits branch creation or updates, add the App to the bypass list or allow `changelog-release`.

**6. Tags from automation.** If another workflow creates the release tags with `GITHUB_TOKEN`, the tag push does not start this workflow. That workflow must push the tag with an App token, or call this workflow with `gh workflow run changelog.yaml -f tag=<tag>`.

**7. First run.**
1. The user commits the files and merges them into the default branch. A tag push runs the workflow file of the tagged commit, so the workflow must exist at that commit.
2. Test without a new release: `gh workflow run changelog.yaml -f tag=<latest stable tag>`. The workflow reads the config from the default branch, so a tag from before the config also works.
3. Optional: push a dev tag. The `Check the tag` job logs a notice, and the changelog job is skipped.
4. For each later release: `git cliff --bumped-version` prints the next version from the commit types. Then run `git tag <version>` and `git push origin <version>`.

## Output

When the work is done, report:

- The files that you added, changed or moved, with their paths. Nothing is committed or staged.
- The settings that you changed, and the settings that the user must still change.
- The output of Step 4, or the reason why you skipped it.
