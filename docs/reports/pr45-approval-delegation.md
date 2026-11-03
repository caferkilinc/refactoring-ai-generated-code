# Project Genesis — PR #45 delegated-approval maintenance

REPORT_SCHEMA_VERSION: 1<br>
TASK_ID: F01-GOV / #1 — PR45-DELEGATION bounded maintenance<br>
OWNER: Cafer Kılınç (@caferkilinc)<br>
DATE: 2026-11-04 (Europe/Istanbul)<br>
BRANCH: chore/1-pr45-approval-delegation<br>
BASE_COMMIT: aa7d2c810a3c19dbc92bd6efa69c517a598dde7e<br>
STATUS: REVIEW_REQUIRED<br>
HANDOFF_STATUS: BLOCKED — activation on trusted main pending<br>
POLICY_ACTIVATED: NO<br>
TARGET_PR: #45<br>
TARGET_SOURCE_HEAD: d923134da4f9f5a2ab55a5f51fbf9415ff717262

## Bounded task and authority

Cafer explicitly asked in this chat to handle the delegation and necessary
policy change here on 2026-11-04. This authorizes the small governance
maintenance described in [ADR 0006](../DECISIONS/0006-pr45-revision-bound-delegation.md).
Burkay's off-platform review/delegation is REPORTED via Cafer, not an
authenticated Burkay GitHub comment. The connected GitHub account is Cafer;
no Burkay identity or approval has been fabricated.

The registry stays Cafer/F00-V0, rotation index 1. This governance preparation
is isolated from the pilot branch and consumes no implementation rotation.
PR #45 remains OPEN, UNMERGED and unchanged at the target SHA. No future task,
F00-V0 merge, acceptance-record write, issue closure or rotation advancement
is authorized by this preparation. Integration/activation remains an explicit
final decision because it changes the trusted main approval policy.

## Implemented and files changed

| File | Change |
|---|---|
| scripts/governance/gate.py | Preserve ordinary Burkay approval; allow Cafer's distinct delegated marker only for the exact PR/repository/task/issue/branch/author/SHA tuple |
| tests/governance/test_pr45_delegation.py | Nine tests with boundary subcases, including full readiness and historical acceptance verification |
| docs/DECISIONS/0006-pr45-revision-bound-delegation.md | Exact task contract, reported provenance, scoped grant, verification and activation boundary |
| docs/DEPENDENCY_MANAGEMENT.md | Link the single revision-bound exception; preserve ordinary policy elsewhere |
| docs/reports/pr45-approval-delegation.md | This maintenance snapshot; root report.md is untouched to avoid conflicts with the exact pilot revision |

No generic delegation infrastructure, workflow edits, task registry changes,
acceptance edits, SRS/architecture changes, source/test-fixture changes or
pilot manifest changes. The exception never approves a new SHA, other PR,
fork, branch, task or author. Approval is still an authenticated API comment,
using `GENESIS-DELEGATE-APPROVED`, never Burkay's owner marker from Cafer.

The first path-policy review rejected an AGENTS.md clarification because that
path is outside F01-GOV's registered allowed paths. The clarification was
placed in the existing dependency policy instead; AGENTS.md remains unchanged.
The existing scope rule was not broadened or bypassed.

## Actual verification

| Command / inspection | Actual outcome |
|---|---|
| git fetch --tags origin with canonical branch refspec | PASS; trusted main unchanged at BASE_COMMIT |
| Live PR #45, account and comment reads | OPEN; target HEAD unchanged; account caferkilinc; zero approval comments |
| python3 -B -m unittest discover -s tests/governance -v | PASS: 111 tests (102 existing plus 9 new), with boundary subcases |
| python3 -B scripts/governance/check_docs.py | PASS |
| python3 -B scripts/governance/security_check.py | PASS; limited credential/private-artifact hygiene only |
| git diff --check and complete new-file whitespace/scope inspection | PASS |
| Read-only live-API evaluation with proposed policy and actual comments | Correctly REJECTED: approval is missing |
| Same evaluation with one explicitly simulated in-memory Cafer delegated marker | PASS: F00-V0's existing predecessor and actual applicable GitHub CI also verified |

The live-API check used 12 authenticated GET requests via gh api. It wrote
nothing to GitHub. Its injected marker existed only in memory and is not an
actual approval or hosted readiness result. Both the negative and positive
outcomes are disclosed. The complete real-data simulation returned:

```text
F00-V0: all 1 mandatory prerequisites accepted; current revision approval and applicable CI verified
```

The output wording reports revision approval without falsely attributing the
delegated marker to Burkay. All missing/failed/skipped check and prerequisite
rejections still apply. The proposal cannot pass itself through a head-defined
policy: existing privileged workflows continue to execute trusted main.

## Activation and remaining blocker

A trusted-main policy update is needed before Cafer's marker can satisfy the
hosted readiness gate. The current registry authorizes F00-V0, so a separate
#1 policy proposal is expected to be blocked by the old active-task rule until
an explicitly authorized integration decision. This proposal does not weaken
that rule, rewrite the registry, manufacture a successful check or authorize
its own governance PR. Review the exact diff and full test evidence before
approving the narrow activation in this chat.

After activation is explicitly authorized, publish the governance policy,
record this exact comment through the actual caferkilinc account on PR #45,
and rerun the trusted-main dependency/readiness workflow:

```text
GENESIS-DELEGATE-APPROVED: d923134da4f9f5a2ab55a5f51fbf9415ff717262
```

That subsequent step is not performed by the current preparation snapshot.
If PR #45 moves, this grant is invalid and a new decision is required. Preserve
source/test manifests and the pilot report. Merge/acceptance and handoff to
Alperen remain separate decisions. ROTATION_ADVANCED: NO.

## Conflict-free activation preparation

The maintenance report is deliberately stored in docs/reports instead of
root report.md. Both policy and pilot branches originally changed root
report.md; merging both could require changing PR #45's source SHA and
invalidate this narrow grant. The root report is restored byte-for-byte to
the approved main baseline in this governance branch. The five final changed
paths are disjoint from PR #45's changed paths. A read-only merge-tree
calculation is used after commit to check composition without updating main
or merging either PR. This is an implementation detail of the approved
maintenance scope, not a new policy exception or changed pilot artifact.
