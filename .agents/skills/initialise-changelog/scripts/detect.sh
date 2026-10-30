#!/bin/bash
# Reads the current repo and prints, as JSON on stdout, the facts that the
# initialise-changelog skill needs before it asks the user anything.
# Read-only: it changes nothing locally or on GitHub.
#
# Usage: detect.sh [repo-dir]

set -euo pipefail

# number of recent first-parent commits on the default branch to sample
SAMPLE_SIZE=100
# Conventional Commits subject: type, optional (scope), optional !, colon, space
CONVENTIONAL_RE='^[a-z]+(\([^)]+\))?!?: '
# a git or GitHub revert subject, which the cliff.toml preprocessor converts
REVERT_RE='^Revert "'
# bytes from the top of CHANGELOG.md to report
CHANGELOG_HEAD_BYTES=400

cd "${1:-.}"
command -v jq >/dev/null || { echo "jq is required" >&2; exit 1; }
ROOT="$(git rev-parse --show-toplevel)" || { echo "Not inside a git repository" >&2; exit 1; }
cd "$ROOT"

ORIGIN="$(git remote get-url origin 2>/dev/null || echo "")"
# owner/repo from https://github.com/o/r(.git) or git@github.com:o/r(.git)
SLUG=""
if [[ "$ORIGIN" =~ github\.com[:/]([^/]+)/([^/]+)$ ]]; then
    SLUG="${BASH_REMATCH[1]}/${BASH_REMATCH[2]%.git}"
fi

DEFAULT_BRANCH="$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's#^origin/##' || true)"
DEFAULT_BRANCH="${DEFAULT_BRANCH:-main}"
echo "Default branch: $DEFAULT_BRANCH" >&2

# tags, grouped by shape
TAGS="$(git tag --list)"
count() { printf '%s\n' "$TAGS" | grep -cE "$1" || true; }
STABLE_V="$(count '^v[0-9]+\.[0-9]+\.[0-9]+$')"
STABLE_BARE="$(count '^[0-9]+\.[0-9]+\.[0-9]+$')"
DEV_DASH="$(count '^v?[0-9]+\.[0-9]+\.[0-9]+-dev$')"
DEV_PEP440="$(count '^v?[0-9]+\.[0-9]+\.[0-9]+\.dev[0-9]+$')"
OTHER_PRE="$(count '^v?[0-9]+\.[0-9]+\.[0-9]+[-.]?(rc|a|b|alpha|beta)')"
LATEST_STABLE="$(git tag --list --sort=-v:refname | grep -E '^v?[0-9]+\.[0-9]+\.[0-9]+$' | head -1 || true)"
OLDEST_STABLE="$(git tag --list --sort=v:refname | grep -E '^v?[0-9]+\.[0-9]+\.[0-9]+$' | head -1 || true)"

# share of recent default-branch commits that git-cliff will keep
REF="origin/$DEFAULT_BRANCH"
git rev-parse --verify -q "$REF" >/dev/null || REF="HEAD"
SUBJECTS="$(git log --first-parent --format=%s -n "$SAMPLE_SIZE" "$REF" 2>/dev/null || true)"
SAMPLED="$(printf '%s\n' "$SUBJECTS" | grep -c . || true)"
CONVENTIONAL="$(printf '%s\n' "$SUBJECTS" | grep -cE "$CONVENTIONAL_RE|$REVERT_RE" || true)"
MERGES="$(printf '%s\n' "$SUBJECTS" | grep -c '^Merge ' || true)"

# existing git-cliff config, changelog and workflows
CLIFF_CONFIG=""
for f in cliff.toml .cliff.toml .config/cliff.toml; do
    [ -f "$f" ] && { CLIFF_CONFIG="$f"; break; }
done
if [ -z "$CLIFF_CONFIG" ] && [ -f pyproject.toml ] && grep -q '^\[tool\.git-cliff' pyproject.toml; then
    CLIFF_CONFIG="pyproject.toml"
fi
CHANGELOG_HEAD=""
[ -f CHANGELOG.md ] && CHANGELOG_HEAD="$(head -c "$CHANGELOG_HEAD_BYTES" CHANGELOG.md)"
WORKFLOWS="$(grep -lE 'git[ -]cliff|create-pull-request' .github/workflows/*.y*ml 2>/dev/null || true)"

# gh prints the error body to stdout on failure, so keep the output only on success
gh_json() { local out; out="$(gh api "$@" 2>/dev/null)" && echo "$out" || echo 'null'; }
# GitHub settings: each call can fail without admin rights or without gh
MERGE_SETTINGS='null'
ACTIONS_REPO='null'
ACTIONS_ORG='null'
APP_VAR='null'
RULES='null'
if [ -n "$SLUG" ] && command -v gh >/dev/null && gh auth status >/dev/null 2>&1; then
    echo "Reading GitHub settings for $SLUG" >&2
    MERGE_SETTINGS="$(gh_json "repos/$SLUG" --jq '{allow_squash_merge, allow_merge_commit, allow_rebase_merge, squash_merge_commit_title, squash_merge_commit_message}')"
    ACTIONS_REPO="$(gh_json "repos/$SLUG/actions/permissions/workflow")"
    ACTIONS_ORG="$(gh_json "orgs/${SLUG%%/*}/actions/permissions/workflow")"
    # active ruleset rules on the default branch, for example required_status_checks
    RULES="$(gh_json "repos/$SLUG/rules/branches/$DEFAULT_BRANCH" --jq '[.[].type] | unique')"
    APP_VAR="$(gh api "repos/$SLUG/actions/variables/CHANGELOG_APP_CLIENT_ID" >/dev/null 2>&1 && echo true || echo false)"
else
    echo "No GitHub remote or no authenticated gh. GitHub settings are unknown." >&2
fi

jq -n \
    --arg root "$ROOT" --arg origin "$ORIGIN" --arg slug "$SLUG" --arg default_branch "$DEFAULT_BRANCH" \
    --argjson stable_v "$STABLE_V" --argjson stable_bare "$STABLE_BARE" \
    --argjson dev_dash "$DEV_DASH" --argjson dev_pep440 "$DEV_PEP440" --argjson other_pre "$OTHER_PRE" \
    --arg latest_stable "$LATEST_STABLE" --arg oldest_stable "$OLDEST_STABLE" \
    --argjson sampled "$SAMPLED" --argjson conventional "$CONVENTIONAL" --argjson merges "$MERGES" \
    --arg cliff_config "$CLIFF_CONFIG" --arg changelog_head "$CHANGELOG_HEAD" \
    --arg release_notes "$([ -f release-notes.json ] && echo true || echo false)" \
    --arg workflows "$WORKFLOWS" \
    --argjson merge_settings "$MERGE_SETTINGS" --argjson actions_repo "$ACTIONS_REPO" \
    --argjson actions_org "$ACTIONS_ORG" --argjson app_var "$APP_VAR" --argjson rules "$RULES" \
    '{
        repo: {root: $root, origin: $origin, github: ($slug != ""), slug: $slug, default_branch: $default_branch},
        tags: {stable_v: $stable_v, stable_bare: $stable_bare, dev_dash: $dev_dash, dev_pep440: $dev_pep440,
               other_prerelease: $other_pre, latest_stable: $latest_stable, oldest_stable: $oldest_stable},
        commits: {sampled: $sampled, conventional: $conventional, merges: $merges},
        existing: {cliff_config: $cliff_config, changelog_head: $changelog_head,
                   release_notes: ($release_notes == "true"), workflows: ($workflows | split("\n") | map(select(. != "")))},
        github: {merge_settings: $merge_settings, actions_repo: $actions_repo, actions_org: $actions_org,
                 changelog_app_var: $app_var, default_branch_rules: $rules}
    }'
