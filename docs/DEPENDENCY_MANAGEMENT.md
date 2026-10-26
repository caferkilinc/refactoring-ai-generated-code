> **Genesis v2.0 transition, owner approved 2026-10-26:** This document describes the legacy issue-based CI evidence mechanism. Fixed developer assignments are superseded by a single active owner; preserved issue prerequisites and independent review remain mandatory. Current transition branch introduces `sequential_execution` in the registry and removes fixed primary/support/reviewer fields. Live issue assignments and metadata are intentionally left intact until the new gate and migration receive independent review. PR #38 may only merge after separate explicit owner approval. All P0 first delivery obligations include Falcon-Mamba, Python/JS/TS and complete PDF reporting.

# Dependency and merge-readiness policy

The reviewed `.github/task-plan.json` maps Plan ID → issue → work package → dynamic authorized owner via sequential_execution → dates/effort → mandatory prerequisites → allowed paths → applicable checks. Issue text and Project cells are planning displays, not sources that can weaken trusted policy. Native issue edges mirror this registry; epics aggregate child work without duplicated effort.

## Two different checks

- `dependency-gate`: currently authorized developer, main target, branch/Task/Plan agreement, complete file scope, native edges and accepted prerequisites.
- `merge-readiness`: all of the above **plus the current PR's** independent Write/Admin approval and successful applicable CI. No review, stale review, a supporting developer's approval, unresolved independent changes requests, draft PR, missing/failed/skipped tests or unrelated check revision may pass.

Both jobs are proposed required checks, not active protection. `merge-readiness` can initially fail while review/tests are pending; that is expected, not a reason to remove it. After review and CI finish, a maintainer re-runs the Dependency gate workflow. Review submission is deliberately **not** wired to an untrusted head-defined workflow or a new write token. A branch may be developed before integration prerequisites pass.

## Trusted policy freshness

Privileged-event jobs check out **the repository's current main**, never PR head code. This fixes reruns that previously reread an old event base SHA and permanently missed later acceptance records. Expected PR head and the checked-out policy SHA are compared to live PR metadata before and after evaluation; drift fails closed and calls for a fresh run. The bootstrap preview runs branch policy with read-only permissions and is explicitly not trusted-main enforcement.

Native issue edits or approval/access revocation can occur after a green run. They do not automatically invalidate a completed GitHub check. Reopen/revoke a prerequisite through a reviewed acceptance/policy change on main, update the dependent branch and rerun both gates immediately before merge. A new event dispatcher with Actions write permissions is not implemented or claimed. Strict up-to-date protection and independent review remain necessary; this is not an instantaneous continuous monitor of mutable GitHub metadata.

## Acceptance of prerequisites

Every prerequisite needs a record in trusted main `.github/acceptance.json` and live evidence of:

1. Issue closed as completed, not not-planned.
2. Matching PR merged to this repository's main; accepted head SHA equals its PR head.
3. Registered Task/Plan/branch and complete changed-file list within allowed scope.
4. Current-revision approval by a Write/Admin teammate outside the PR author and actual GitHub-linked commit authors/committers; unresolved independent changes requests block.
5. All applicable GitHub Actions checks completed with **success**, not missing/skipped/neutral.
6. A nonempty list of HTTPS evidence URLs without embedded credentials, independently assessed against the task acceptance criteria.

Illustrative schema, not a real acceptance:

```json
{"schema_version":1,"accepted":{"8":{"pr":101,"head_sha":"actual-accepted-pr-head","evidence":["https://github.com/OWNER/REPO/pull/101"]}}}
```

Optional `ci_sha` may identify that PR's head or its actual merged commit when check placement requires it; arbitrary commits cannot supply CI proof. On the audited bootstrap PR the hosted checks were confirmed on its head SHA. Evidence URLs are reviewed attestations, not automated semantic proof of a research result.

Governance maintenance must be an explicitly authorized sequential task; historically it used `chore/1-...`, `Task: #1`, `Plan: F01-GOV`, even after #1 closes. Ordinary application tasks cannot change governance scripts/tests, policy registries, CODEOWNERS or protected workflows through a broad `tests/` path. #10 may define only application CI workflow paths; governance workflow changes require #1. Policy changes require independent review and activated main protection.

## Real checks for each deliverable

| Task / scope | Required application evidence | Who supplies the real workflow |
|---|---|---|
| #9 Java pilot | `pilot-checks`, real Maven/JUnit pilot build/tests | #9 may add `.github/workflows/pilot-checks.yml`; no Python environment dependency is invented |
| #11 CIR/API contracts | `contract-checks`, actual schema/fixture validation | #11 may add `.github/workflows/contract-checks.yml` so early contracts need not wait for #10 |
| #10 environment | backend-checks and frontend-checks | #10 supplies real pinned packages, lockfiles, test commands and application CI |
| #22, #30, #31, #34, #35 mixed delivery / E2E | backend-checks and frontend-checks | Actual app checks from #10; mixed/E2E task evidence is also reviewed |
| Any PR changing backend or frontend | Adds corresponding check based on actual changed paths | A frontend task label cannot hide backend code |
| Schema paths / contract tests | Adds contract-checks | Real contract tests; no fake green command |

No application, pilot or contract workflow is claimed implemented by this setup. Their tasks must provide actual executable checks before readiness/acceptance can pass. The extra #21 → #10 integration edge makes the UI's real environment prerequisite explicit while mock development can proceed independently.

## Synchronization and drift

Issue graph sync performs a complete read preflight before the first write; unexpected parents/edges stop the run. It only adds expected missing links. GitHub writes are not a transaction: an API/network failure during the write stage can still leave a partial result. Re-run the idempotent sync after fixing the cause, then audit; do not erase history or delete unrelated edges.

`python3 scripts/governance/audit_plan.py` audits all registered task metadata bodies, six parent lists and native prerequisites with read-only API requests. After merge, the owner may run Actions → Live plan audit on main. This is a diagnostic, not a required merge check: dispatch-only workflow jobs are not eligible required PR checks. Personal Project date/effort cells still need a separate board comparison; `GITHUB_TOKEN` access to a repository does not grant access to a private personal Project.

## Activation

Bootstrap #38 first needs Burkay's current independent approval and successful actual CI; a separate affirmative owner merge decision remains pending. After separately authorized merge, run real canary cases including missing prerequisite, accepted dependency, old-event rerun, missing/failed app CI, primary/support approval rejection, review resolution and current independent approval. Only then activate the five proven proposed required names in [protection JSON](../.github/branch-protection.proposed.json), with current-branch checks, stale review dismissal, CODEOWNERS, resolved conversations, admin enforcement and no force push/deletion.

The bootstrap cannot test a trusted-main workflow absent from main. Unit tests prove engine behavior with isolated API fixtures; hosted bootstrap previews prove read-only API compatibility. Neither demonstrates that GitHub currently blocks merge. See [operational audit](OPERATIONAL_AUDIT.md) for verified findings, fixes and residual risks.
