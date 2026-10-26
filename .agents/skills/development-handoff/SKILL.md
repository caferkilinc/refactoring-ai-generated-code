---
name: development-handoff
description: Execute a single orchestrator-authorized implementation or repair task, verify acceptance, and prepare an evidence-based report for human Git review/publication.
---

# Single-task handoff (Project Genesis v2.0)

Trigger only when one authorized developer receives a concrete, bounded task with milestone/ID, approved source and accepted baseline. This skill never grants task selection or merge authority.

1. **Preflight:** inspect repository root, branch, HEAD, remote/upstream, working tree and expected prior accepted commit. Stop on divergence, unknown local changes or unapproved branch transitions. No reset/clean/force-push.
2. **Authorization:** confirm owner matches `sequential_execution` and orchestrator task contract, prerequisites accepted and change scope defined. Old fixed GitHub assignees do not authorize coding.
3. **Context:** read relevant `AGENTS.md`, approved SRS/architecture sections, `docs/PROJECT_STATUS.md`, roadmap, touched code/tests and last handoff only where needed. Do not blindly ingest all repository files.
4. **Implement:** make the smallest correct change; preserve contracts, owner permissions, V0/frozen tests, SAST and isolation controls.
5. **Verify:** run actual focused and applicable integration checks, mark PASS/FAIL/NOT_RUN/NOT_APPLICABLE from evidence; avoid repeated speculative repair after two attempts without new root-cause evidence.
6. **Review:** inspect real diff and scope, check protected files, secrets, accidental generated artifacts, security and regression risk. Never silently discard user work.
7. **Report:** update reusable project records only when justified. `report.md` includes task/owner/branch/base SHA, actual changes, files, FR/NFR coverage, criterion-by-criterion evidence, commands/results, blockers, conditional next owner and `PENDING_PUSH_CONFIRMATION` or `BLOCKED`. Do not invent the SHA of the containing commit.
8. **Human publication:** provide changed files and safe review/commit/push guidance. Human performs independent PR review and authorized publication, then submits final SHA/report to orchestrator. Only the orchestrator accepts handoff.
9. **STOP.** Never begin next milestone/task, advance rotation, waive review, merge PR #38 or claim release readiness.
