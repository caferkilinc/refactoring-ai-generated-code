# Genesis v2.0 migration acceptance checklist

**Record date:** 2026-10-27. **Status:** REVIEW_REQUIRED — not a completed implementation handoff.  
**Owner-approved scope:** Master Architecture v2.0 + Development Guide v2.0; retain original 31 technical issue identities and 54 native edges, with 3 new P0 issues and 15 *planned* links (34/69 total). Fixed assignments are to be removed after reviewed migration. Java, Python, JS, TS, C#/Roslyn, Go, C++ and real local Falcon-Mamba 7B, full HTML/PDF/ZIP/history are mandatory P0; five-person rotation begins with Burkay.  
**Base evidence:** PR #38 (`chore/1-team-workflow`) is open bootstrap work, authored before Genesis; it does **not** count as Cafer's Genesis handoff. `main` is the accepted integration branch.

## Changes prepared on review branch

- `docs/SRS.md` and `docs/SRS_EN.md`: bilingual v0.4 ID-aligned review drafts (FR-001–062, NFR-01–17). **The owner has approved the source and scope, not yet signed off the two completed documents.**
- `.github/task-plan.json`: preserved 31 original task records and all 54 native prerequisite edges; added #40–#42 with 15 planned edges; removed fixed `owner/support/reviewer`; all six newly mandatory tasks promoted to P0; explicit sequential owner state initialized to Burkay.
- `scripts/governance/gate.py`: uses selected active task/owner instead of old primary/support, excludes PR author and any commit authors/committers from independent review, protects governance changes, retains a *strict* PR #38 legacy bootstrap exception for independent review but never advances the new rotation.
- `scripts/governance/audit_plan.py`: explicit phased live-assignment migration; must not silently treat old GitHub assignees as authoritative.
- `scripts/governance/workload.py` and `docs/TEAM_WORKLOAD.md`: no fixed developer workloads; historic window/effort estimates only.
- `scripts/governance/migrate_assignments.py` plus `tests/governance/test_assignment_migration.py`: dry-run-first full-graph live issue assignment cleaner, inert until the accepted policy reaches `main`, exact owner approval and a clean repository state. Never run from this draft PR.
- `tests/governance/`: verify rotator constraints, invalid assignee/policy cases, current independent review, GitHub prerequisites and bilingual SRS parity.
- `AGENTS.md` and `.agents/skills/development-handoff/SKILL.md`: concise persistent Codex instructions and bounded human-reviewed handoff workflow; availability in each developer's Codex IDE must still be verified.
- `README.md`, `CONTRIBUTING.md`, `docs/ARCHITECTURE.md`, `docs/DEVELOPMENT_ROADMAP.md`, `docs/PROJECT_STATUS.md`, `docs/TEAM_WORKFLOW.md`, and existing dependency documentation: align mandatory delivery, nonexclusive module expertise and merge restrictions.

## Blocking sequence / do not skip

1. Verify the migration draft's source diff, 34-task / 69-edge proposed invariant plus independent original-31/original-54 preservation, route and approval restrictions, security hygiene and actual applicable test execution. Do **not** label tests PASS without a run.
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
- The SRS translations have 62 FR and 17 NFR with aligned IDs/priorities but do not yet possess separately recorded final text sign-off. Requirements must be reviewed for semantic parity as well as ID equality.

## Handoff integrity

**Current authorized implementation owner:** Burkay. **Next only if accepted:** Cafer.  
**Last confirmed Genesis handoff:** NONE.  
**Merged into main:** NO.  
**PR #38 owner merge approval:** NOT_GRANTED.  
**This migration preparation:** documentation and safety governance work performed via authorized GitHub tooling, **not an execution by a developer's Codex**, and must not be misreported as an accepted Burkay or Cafer task.

## 2026-10-27 — additional mandatory C#/Go/C++ migration

- Owner approved *all seven* Java/Python/JS/TS/C#/Go/C++ adapters for first delivery; original 31 issues and 54 native edges remain. New issues #40–#42 exist without assignees; new planned graph has 34 tasks / 69 edges. See SRS v0.4.0.
- **Native GitHub graph incomplete:** place #40–#42 under epic #7; add three blocked_by links to each (#11/#16/#26), add #40/#41/#42 to #34, and add #20/#31/#34 to #35. Validate entire graph and rerun live governance audit without deleting legacy edges. Do not claim sync until tool/API evidence confirms it.
- This extends the previous 31-task assignment-clearing migration: `migrate_assignments.py` dry-run assumptions (31 issues, 54 edges) are **STALE** for expanded graph. Update/test its supported task-count logic before any live `--apply`; do not execute old version on new plan.
- PR #38 remains open, no merge. Burkay is owner-designated technical lead and audit coordinator, but GitHub records Cafer as author; contributor-independent review and separate owner permission remain mandatory. Re-run all checks after these revisions.

## 2026-10-27 scope extension — additional review gates

Three new P0 issues #40 C#/Roslyn, #41 Go and #42 C++/Clang are recorded without permanent developer assignment. The existing 31 tasks and 54 native edges are preserved; the reviewed plan intends **34 tasks, 69 edges**.

Native GitHub parent (#7) and blocked-by relationships for the new tasks, plus changed #34 and #35 prerequisites, still require guarded synchronization and independent live audit. GitHub issue creation and updating task-plan.json do NOT establish native graph linkage. Do not run live assignment migration until the new graph is VERIFIED and the governance policy is reviewed and accepted.

Turkish/English SRS v0.4 contain 62 FR and 17 NFR apiece (review draft, no final sign-off). PR #38 is still open and **must not be merged** without independent review, passing checks and a separate explicit owner merge permission.
