---
name: development-handoff
description: Execute one authorized Project Genesis implementation or repair task, verify its criteria, and prepare an evidence-based handoff for human review and publication.
---

# Single-task handoff (Project Genesis)

Trigger only when one authorized developer receives a concrete, bounded task with milestone/ID, approved source and accepted baseline. This skill never grants task selection or merge authority.

1. **Preflight:** inspect repository root, branch, HEAD, remote/upstream, working tree and expected prior accepted commit. Stop on divergence, unknown local changes or unapproved branch transitions. No reset/clean/force-push.
2. **Authorization:** identify the policy active on verified `main` through [AGENTS.md](../../../AGENTS.md). Confirm the contract and owner against `sequential_execution`, accepted prerequisites and scope. Under active v3, the registered developer explicitly authorizes execution. A concurrent protected maintenance task needs a separate recorded owner exception.
3. **Context:** read relevant `AGENTS.md`, approved SRS/architecture sections, `docs/PROJECT_STATUS.md`, roadmap, touched code/tests and last handoff only where needed. Do not blindly ingest all repository files.
4. **Implement:** make the smallest correct change; preserve contracts, owner permissions, V0/frozen tests, SAST and isolation controls.
5. **Verify:** run actual focused and applicable integration checks, mark PASS/FAIL/NOT_RUN/NOT_APPLICABLE from evidence; avoid repeated speculative repair after two attempts without new root-cause evidence.
6. **Review:** inspect real diff and scope, check protected files, secrets, accidental generated artifacts, security and regression risk. Never silently discard user work.
7. **Report:** update reusable project records only when justified. `report.md` includes task/owner/branch/base SHA, actual changes, files, FR/NFR coverage, criterion-by-criterion evidence, commands/results, blockers, conditional next owner and `PENDING_PUSH_CONFIRMATION` or `BLOCKED`. Do not invent the SHA of the containing commit.
8. **Human publication:** provide the actual diff and evidence, then stop for explicit authorization of publication scope. Under active v3 the developer records the task- and head-bound approval defined in the [canonical protocol](../../../docs/governance/PROJECT_GENESIS_CODEX_NATIVE_PROTOCOL_V3.md). Protected changes also require owner authorization. Preserve hosted review and CI requirements. Keep approval, hosted verification, merge and independent acceptance as separate records.
9. **STOP.** Handoff acceptance and rotation are separately reviewed operations. Start another task only with its own verified authorization.
