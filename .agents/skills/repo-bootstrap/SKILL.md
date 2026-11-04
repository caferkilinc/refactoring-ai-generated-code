---
name: repo-bootstrap
description: Verify and safely prepare the canonical Project Genesis Git checkout before an authorized task. Use for repository identity, source revision and worktree readiness.
---

# Project Genesis repository bootstrap

## Inspect the checkout

1. Detect the OS and active shell. Use its native syntax on Windows, macOS or Linux. Check `git --version` and verify support for the options used below. Resolve the repository root with `git rev-parse --show-toplevel`. Read applicable [AGENTS.md](../../../AGENTS.md) instructions and check that the selected worktree and branch match the requested scope.
2. Capture the current branch (`git branch --show-current`), `HEAD`, configured upstream if present, and `git worktree list --porcelain`. Resolve Git state paths with `git rev-parse --git-path` and check for index locks, merges, rebases, cherry-picks, reverts or sequencer state. Capture staged and unstaged diffs separately and inventory untracked and relevant ignored paths with `git status --porcelain=v1 --untracked-files=all --ignored=matching`. Record enough starting state to detect later changes without exposing ignored secrets.
3. Inspect applicable `.gitattributes`, including nested rules and effective attributes on affected paths. Review the origins and effective values of `core.autocrlf`, `core.eol` and relevant filters. Use `git check-attr` and `git ls-files --eol` to explain conversions. An LF/CRLF warning describes possible conversion. For byte-sensitive files, compare actual file bytes with the pinned Git blob using `git hash-object --no-filters -- path` or verify the approved manifest's SHA-256. Avoid renormalization or configuration changes.

## Verify the canonical source

- Confirm the effective fetch URL with `git remote get-url` and `git ls-remote --get-url`. Follow the exact repository transfer identity in [repository_identity.py](../../../scripts/governance/repository_identity.py): original `caferkilinc/refactoring-ai-generated-code`, proposed destination `refactoring-ai-code/refactoring-ai-generated-code`, immutable GitHub repository ID `1391020028`. Destination use requires a matching authenticated API repository ID; a name, redirect or copied repository alone is insufficient. The selected HTTPS/SSH origin and GitHub workflow identity must agree. Check relevant URL rewrites and transport settings without printing credentials. A remote name alone establishes no identity. Block on a missing or unverified canonical remote, transport failure, unexpected redirects or unsafe configuration. This proposed bridge grants no transfer or policy activation authority itself.
- Query live `refs/heads/main` via `git ls-remote --exit-code --refs`. If the commit is unavailable locally or fetching is requested, use a verified remote, an explicit source-only refspec and empty `--refmap=` to avoid configured remote-tracking writes. A suitable command is `git -c fetch.prune=false -c fetch.pruneTags=false fetch --no-prune --no-tags --no-recurse-submodules --refmap= REMOTE refs/heads/main`, with `REMOTE` replaced by the verified remote name. Compare the fetched commit in `FETCH_HEAD` with a fresh live query. Fetch only additional refs needed for the task with equivalent safeguards. Stop on an unexplained ref change or an unverifiable snapshot.
- Keep local `HEAD`, local `main`, live canonical `main` and the upstream or corresponding remote branch distinct. Use `git rev-list --left-right --count LOCAL...REMOTE` or ancestry checks after verifying the compared commits. A topic branch can be ahead of its base by design. Compare it with its intended upstream and the approved baseline. A missing upstream is evidence to report and may be expected for a new or explicitly scoped migration branch. Check the matching remote ref separately where it exists. Block on incompatible divergence or an unverified base. This preflight fetches evidence and preserves the worktree. Any checkout or fast-forward requires its own safe, authorized conditions.
- From the verified main object read [task-plan.json](../../../.github/task-plan.json) and [acceptance.json](../../../.github/acceptance.json), for example with `git show SHA:.github/task-plan.json`. Report the registered active task and developer from `sequential_execution`. Migration scope and authorization are separate. Legacy issue assignees and branch-local policy drafts cannot grant authority.

## Report readiness

Return the result, repository root, OS/shell and Git version, branch and local SHA, live main SHA, upstream/ref comparison, worktrees, Git operation status, line-ending findings, initial changed paths and the observed active task/developer.

| Result | Condition |
|---|---|
| `READY` | Identity, required source and baseline verified, worktree clean for the task. |
| `READY_WITH_EXISTING_CHANGES` | Same checks passed. Existing changes have known provenance, can be preserved and do not conflict with the authorized work. Keep them separate in later diff review. |
| `BLOCKED` | Required evidence is missing, changes are unknown or conflicting, an operation is in progress, or preparation would overwrite work. Report the exact condition and preserve the checkout. |

Keep existing work in place. Do not reset, clean, stash, rebase, merge, change remote configuration or force-push as part of preflight. Readiness is an input to the separate authorization step in [development-handoff](../development-handoff/SKILL.md).
