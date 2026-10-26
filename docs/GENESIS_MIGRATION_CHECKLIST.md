# Genesis v2.0 migration acceptance checklist

**Record date:** 2026-10-26. **Status:** REVIEW_REQUIRED — not a completed implementation handoff.  
**Owner-approved scope:** Master Architecture v2.0 + Development Guide v2.0; 31 technical issue identities and 54 dependency edges retained; remove fixed implementation assignments; all first-delivery Java/Python/JS/TS, Local Falcon-Mamba 7B, and full HTML/PDF capabilities mandatory P0; five-person rotation begins with Burkay.  
**Base evidence:** PR #38 (`chore/1-team-workflow`) is open bootstrap work, authored before Genesis; it does **not** count as Cafer's Genesis handoff. `main` is the accepted integration branch.

## Changes prepared on review branch

- `docs/SRS.md` and `docs/SRS_EN.md`: bilingual, ID-aligned review drafts (FR-001–057, NFR-01–15). **The owner has approved the source and scope, not yet signed off the two completed documents.**
- `.github/task-plan.json`: preserved 31 task records, native issue numbers, dependency IDs and 54 prerequisite edges; removed fixed `owner/support/reviewer`; all six newly mandatory tasks promoted to P0; explicit sequential owner state initialized to Burkay.
- `scripts/governance/gate.py`: uses selected active task/owner instead of old primary/support, excludes PR author and any commit authors/committers from independent review, protects governance changes, retains a *strict* PR #38 legacy bootstrap exception for independent review but never advances the new rotation.
- `scripts/governance/audit_plan.py`: explicit phased live-assignment migration; must not silently treat old GitHub assignees as authoritative.
- `scripts/governance/workload.py` and `docs/TEAM_WORKLOAD.md`: no fixed developer workloads; historic window/effort estimates only.
- `scripts/governance/migrate_assignments.py` plus `tests/governance/test_assignment_migration.py`: dry-run-first full-graph live issue assignment cleaner, inert until the accepted policy reaches `main`, exact owner approval and a clean repository state. Never run from this draft PR.
- `tests/governance/`: verify rotator constraints, invalid assignee/policy cases, current independent review, GitHub prerequisites and bilingual SRS parity.
- `AGENTS.md` and `.agents/skills/development-handoff/SKILL.md`: concise persistent Codex instructions and bounded human-reviewed handoff workflow; availability in each developer's Codex IDE must still be verified.
- `README.md`, `CONTRIBUTING.md`, `docs/ARCHITECTURE.md`, `docs/DEVELOPMENT_ROADMAP.md`, `docs/PROJECT_STATUS.md`, `docs/TEAM_WORKFLOW.md`, and existing dependency documentation: align mandatory delivery, nonexclusive module expertise and merge restrictions.

## Blocking sequence / do not skip

1. Verify the migration draft's source diff, 31-task / 54-edge invariant, route and approval restrictions, security hygiene and actual applicable test execution. Do **not** label tests PASS without a run.
2. Independent, contributor-free code review of migration and PR #38 on the actual current commits. Reviewer requests and old approvals do not equal accepted review.
3. Confirm branch-protection/CI applicability and finish PR #38 compatibility migration without removing existing code, issue history or Git dependencies.
4. **Request a separate, explicit project owner decision for final merging of PR #38. No approval from earlier chat text is a standing merge authorization.**
5. Only after accepted governance policy reaches main, safely migrate live issue assignees and fixed primary/support/reviewer body fields using the reviewed script's default dry-run followed by separately authorized `--apply --owner-approved` on a clean `main` checkout. Require a dry-run reconciliation and preserve issue titles, objective, acceptance, priority, timestamps, native subissues and dependency edges. If partial failure occurs, stop and report; do not guess restored state.
6. Run live audit and GitHub action canary on main (including out-of-turn user, missing acceptance, wrong branch, stale review, policy edits and duplicate handoff). Do not disable a failing gate to force acceptance.
7. Confirm finalized bilingual SRS with owner, real runtime/GPU/provider access, reproducible test/demo plan and handoff readiness. Burkay starts first authorized executable task; Cafer remains conditional successor until accepted publication.

## Open blocking risks

- Until `main` contains the new gate, live issue assignee changes are **blocked** by the old trusted governance mechanism. No automatic task reassignment occurs from the draft registry.
- Current date/deadline estimates were made for parallel developer ownership, not the now-sequential 31-task workflow. Reforecast the critical path; do not invent a percent completion or guarantee on-time delivery.
- Falcon-Mamba exact model runtime/quantization, GPU availability, provider permission, token costs and concrete acceptance workload remain unverified. A missing capability is a real release blocker, not an excuse to demote the first-delivery scope.
- Historical `docs/SETUP_REPORT.md` and `docs/OPERATIONAL_AUDIT.md` may retain previous owners/P1 facts; interpret those as past audit evidence, not current approved scope.
- The SRS translations have aligned IDs/priorities but do not yet possess recorded final owner sign-off. Requirements must be reviewed for semantic parity as well as ID equality.

## Handoff integrity

**Current authorized implementation owner:** Burkay. **Next only if accepted:** Cafer.  
**Last confirmed Genesis handoff:** NONE.  
**Merged into main:** NO.  
**PR #38 owner merge approval:** NOT_GRANTED.  
**This migration preparation:** documentation and safety governance work performed via authorized GitHub tooling, **not an execution by a developer's Codex**, and must not be misreported as an accepted Burkay or Cafer task.
