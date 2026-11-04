---
name: development-handoff
description: Execute one authorized Project Genesis implementation or repair task, verify its criteria, and prepare an evidence-based handoff for human review and publication.
---

# Single-task handoff (Project Genesis)

Trigger only when one authorized developer receives a concrete, bounded task with milestone/ID, approved source and accepted baseline. This skill never grants task selection or merge authority.

Use [task-execution](../task-execution/SKILL.md) as the bounded implementation entry point. When it refers here, use the reporting, human review and stop guidance without restarting execution.

1. **Preflight:** use [repo-bootstrap](../repo-bootstrap/SKILL.md) to verify repository identity, source and worktree readiness. Stop on `BLOCKED` and retain the starting inventory for diff review.
2. **Authorization:** identify the policy active on verified `main` through [AGENTS.md](../../../AGENTS.md). Confirm the contract and owner against `sequential_execution`, accepted prerequisites and scope. Under active v3, the registered developer explicitly authorizes execution. A concurrent protected maintenance task needs a separate recorded owner exception.
3. **Context:** use [task-context](../task-context/SKILL.md) to recover the authorized task's requirements, prerequisites, relevant code and tests, and source provenance.
4. **Implement:** make the smallest correct change; preserve contracts, owner permissions, V0/frozen tests, SAST and isolation controls.
5. **Verify:** use [verification](../verification/SKILL.md) to select and run applicable checks, preserve protected inputs, and record actual results.
6. **Review:** inspect real diff and scope, check protected files, secrets, accidental generated artifacts, security and regression risk. Never silently discard user work.
7. **Report:** update reusable project records only when justified. Use root `report.md` only within authorized scope. Otherwise use a task-scoped report. Include task/owner/branch/base SHA, actual changes, files, FR/NFR coverage, criterion-by-criterion evidence, commands/results, blockers, conditional next owner and `PENDING_PUSH_CONFIRMATION` or `BLOCKED`. Do not invent the SHA of the containing commit.
8. **Human publication:** provide the actual diff, review ID and evidence. Under active v3, an explicit `PUSHLA` for that review enters [safe-publish](../safe-publish/SKILL.md) once. Protected owner authorization and hosted CI or review rules still apply. Keep approval, hosted verification, merge and independent acceptance as separate records.
9. **STOP.** Handoff acceptance and rotation are separately reviewed operations. Start another task only with its own verified authorization.
