# Dependency and merge-readiness policy

The [v3 protocol](governance/PROJECT_GENESIS_CODEX_NATIVE_PROTOCOL_V3.md) defines the proposed activation and authority model. The current trusted `main` and actual GitHub settings govern until activation.

The reviewed `.github/task-plan.json` maps Plan ID → issue → work package → dynamic authorized owner via sequential_execution → dates/effort → mandatory prerequisites → allowed paths → applicable checks. Issue text and Project cells are planning displays, not sources that can weaken trusted policy. Native issue edges mirror this registry; epics aggregate child work without duplicated effort.

## Two different checks

- `dependency-gate`: currently authorized developer, main target, branch/Task/Plan agreement, complete file scope, native edges and accepted prerequisites.
- `merge-readiness`: all of the above plus authenticated exact-head developer approval and successful applicable CI under active v3. Known protected changes require a separate exact-head owner approval. GitHub enforces required independent reviews and conversation resolution separately. Draft PRs and missing, failed, skipped or unrelated CI block readiness.

Both jobs are proposed required checks. Verify actual hosted configuration before relying on them for merge protection. After approval and CI finish, an authorized maintainer reruns the Dependency gate workflow against the current revision. The workflow uses read-only permissions and trusted code.

## Trusted policy freshness

Privileged-event jobs check out **the repository's current main**, never PR head code. This fixes reruns that previously reread an old event base SHA and permanently missed later acceptance records. Expected PR head and the checked-out policy SHA are compared to live PR metadata before and after evaluation; drift fails closed and calls for a fresh run. The bootstrap preview runs branch policy with read-only permissions and is explicitly not trusted-main enforcement.

Native issue edits or approval/access revocation can occur after a green run. They do not automatically invalidate a completed GitHub check. Reopen/revoke a prerequisite through a reviewed acceptance/policy change on main, update the dependent branch and rerun both gates immediately before merge. A new event dispatcher with Actions write permissions is not implemented or claimed. Strict up-to-date protection and independent review remain necessary; this is not an instantaneous continuous monitor of mutable GitHub metadata.

## Acceptance of prerequisites

Every prerequisite needs a record in trusted main `.github/acceptance.json` and live evidence of:

1. Issue closed as completed, not not-planned.
2. Matching PR merged to this repository's main; accepted head SHA equals its PR head.
3. Registered Task/Plan/branch and complete changed-file list within allowed scope.
4. Revision-bound publication authority. New v3 records name the authorized developer in `developer`, while historical records use their original owner or scoped delegation evidence. Required GitHub reviews remain separately verified.
5. All applicable GitHub Actions checks completed with **success**, not missing/skipped/neutral.
6. A nonempty list of HTTPS evidence URLs without embedded credentials, independently assessed against the task acceptance criteria.

Illustrative schema, not a real acceptance:

```json
{"pr":101,"head_sha":"actual-accepted-pr-head","developer":"authorized-login","evidence":["https://github.com/OWNER/REPO/pull/101"]}
```

Optional `ci_sha` may identify that PR's head or its actual merged commit when check placement requires it; arbitrary commits cannot supply CI proof. On the audited bootstrap PR the hosted checks were confirmed on its head SHA. Evidence URLs are reviewed attestations, not automated semantic proof of a research result.

Governance maintenance uses a separately authorized `chore/1-...` branch, `Task: #1` and `Plan: F01-GOV`. Working during another developer's turn requires an explicit protected exception under the trusted policy. Governance policy paths require #1 and its applicable scope. A task-authorized application workflow still needs protected owner approval because it changes CI. Policy changes require independent review and verified main protection.

## Real checks for each deliverable

| Task / scope | Required application evidence | Who supplies the real workflow |
|---|---|---|
| #9 Java pilot | `pilot-checks`, real Maven/JUnit pilot build/tests | #9 may add `.github/workflows/pilot-checks.yml`; no Python environment dependency is invented |
| #11 CIR/API contracts | `contract-checks`, actual schema/fixture validation | #11 may add `.github/workflows/contract-checks.yml` so early contracts need not wait for #10 |
| #10 environment | backend-checks and frontend-checks | #10 supplies real pinned packages, lockfiles, test commands and application CI |
| #22, #30, #31, #34, #35 mixed delivery / E2E | backend-checks and frontend-checks | Actual app checks from #10; mixed/E2E task evidence is also reviewed |
| Any PR changing backend or frontend | Adds corresponding check based on actual changed paths | A frontend task label cannot hide backend code |
| Schema paths / contract tests | Adds contract-checks | Real contract tests; no fake green command |

Verify each required workflow's existence, runtime and result on the relevant revision before granting readiness or acceptance. The #21 → #10 integration edge records the UI's environment prerequisite.

## Synchronization and drift

Issue graph sync performs a complete read preflight before the first write; unexpected parents/edges stop the run. It only adds expected missing links. GitHub writes are not a transaction: an API/network failure during the write stage can still leave a partial result. Re-run the idempotent sync after fixing the cause, then audit; do not erase history or delete unrelated edges.

`python3 scripts/governance/audit_plan.py` audits all registered task metadata bodies, six parent lists and native prerequisites with read-only API requests. After merge, the owner may run Actions → Live plan audit on main. This is a diagnostic, not a required merge check: dispatch-only workflow jobs are not eligible required PR checks. Personal Project date/effort cells still need a separate board comparison; `GITHUB_TOKEN` access to a repository does not grant access to a private personal Project.

## Activation

PR #38 is a historical bootstrap. Before activating v3, obtain the separate protected migration decision and verify the actual rules for `main`. Use the five required names in [protection JSON](../.github/branch-protection.proposed.json) with strict current-branch checks, stale review dismissal, CODEOWNERS, resolved conversations, admin enforcement and no force push/deletion. Retain any additional effective protections. Run hosted positive and negative cases for exact-head approval, CI, protected scope and policy freshness.

The bootstrap cannot test a trusted-main workflow absent from main. Unit tests prove engine behavior with isolated API fixtures; hosted bootstrap previews prove read-only API compatibility. Neither demonstrates that GitHub currently blocks merge. See [operational audit](OPERATIONAL_AUDIT.md) for verified findings, fixes and residual risks.

## Historical PR #45 delegation

[ADR 0006](DECISIONS/0006-pr45-revision-bound-delegation.md) preserves Cafer's authenticated approval for the accepted PR #45 revision only. Keep its original evidence and CI when rechecking the F00-V0 acceptance.
