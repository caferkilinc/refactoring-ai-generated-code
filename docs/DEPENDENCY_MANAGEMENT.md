# Dependency management and acceptance

`.github/task-plan.json` is the reviewed registry of Plan ID → real issue → parent work package → owner/support/reviewer → date/effort → integration prerequisites → allowed paths → applicable checks. Native issue links mirror that registry. Epics aggregate child work and have no duplicated effort. See the [full edge list](DEVELOPMENT_ROADMAP.md).

The gate runs on `pull_request_target` using **only the base SHA** and a read-only token. It reads live PR/issue metadata but never executes PR head code. PR text alone cannot redefine task scope, prerequisites or acceptance. Branch number, one `Task: #N`, one `Plan: ID`, registered issue and affected paths must agree. Unknown tasks, missing API data, cycles, extra/missing native dependency edges and failed evidence checks fail closed.

Every mandatory prerequisite needs a record in trusted main `.github/acceptance.json`, plus live verification of:

1. Issue closed as completed, not merely closed as not-planned.
2. Linked PR merged to this repository's main; accepted SHA equals its head.
3. PR branch/body match the prerequisite task and changed paths are allowed.
4. An independent teammate with current Write/Admin approval on that exact revision; stale/self/dismissed or superseded approvals do not qualify.
5. Required GitHub Actions checks completed successfully; missing, skipped or failing checks cannot qualify.
6. HTTPS evidence links reviewed by the maintainer against task-specific acceptance criteria.

Example schema (illustrative values, **not** an existing acceptance):

```json
{"schema_version":1,"accepted":{"8":{"pr":101,"head_sha":"actual-merged-pr-head-sha","evidence":["https://github.com/OWNER/REPO/pull/101"]}}}
```

The real registry starts empty; no product work is accepted. The evidence URLs are attestations reviewed by people, not automated semantic proof that arbitrary linked artefacts satisfy the scientific protocol. New accepted records require an independently reviewed governance PR; this trust boundary must be protected by branch rules. Historical required checks are recorded in the registry and may evolve through reviewed policy changes.

A blocked merge does not prevent topic-branch development using approved contract fixtures. Scope extensions and cross-cutting tasks require prior reviewed registry updates. F07B is P1 and is not a transitive prerequisite of P0.

After a prerequisite is accepted, use Actions → failed Dependency gate run → Re-run all jobs, or push a normal new commit to the dependent branch. Closing an issue alone does not trigger reevaluation or acceptance. `workflow_dispatch` graph sync is available after the workflow reaches main; it only creates missing expected edges, refuses deletions/reparenting and is owner-only.

## Bootstrap and protection activation

The setup PR cannot use a base policy absent from main. Its governance engine has isolated positive/negative tests; the bootstrap review is manual. Once approved and merged, open a real numbered canary PR and confirm `dependency-gate` runs from main with expected pass/fail results before making it required. Do not mark a fake development task complete to test this.

The proposed [protection JSON](../.github/branch-protection.proposed.json) requires an independent code-owner approval, stale approval dismissal, conversation resolution, current branch checks, no force push/deletion and admin enforcement. It is **not active**. Activate only after explicit owner approval and live checks; never lock the repository against a check that has not run.

The 22 unit scenarios verify engine behavior with isolated API fixtures. They do not prove that GitHub currently blocks merge. Live CI/review merge prevention remains an activation/verification step until the proposed protections are approved.
