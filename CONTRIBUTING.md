# Contribution workflow — Project Genesis v2.0

**No preassigned technical task owner.** Each authorized implementation developer receives **one** current task from the main orchestrator in sequence: Burkay → Cafer → Alperen Enes Yaman → İsmail → Taha Uğur Toyran → repeat. Historical work-package ownership and GitHub issue assignees do not authorize implementation. Task contracts identify the required Plan ID, technical GitHub issue, accepted baseline, scope and acceptance checks.

1. Orchestrator selects one READY task after checking accepted prerequisites and state.
2. Authorized developer checks local worktree/HEAD/upstream/remote; safely syncs `main` (only clean and fast-forward when appropriate).
3. Use issue-numbered topic branch (`feature/<issue>-slug`, `fix/<issue>-slug`, `docs/<issue>-slug`, `test/<issue>-slug`, `chore/<issue>-slug`) for independent PR review. Only the current owner implements; the existence of a topic branch does not create concurrent authorization.
4. Implement the bounded task, run real task-specific checks, review scope/secrets, produce a concise `report.md` with `PENDING_PUSH_CONFIRMATION`. Codex MUST stop after one task and cannot claim push/merge.
5. Human reviews and publishes to topic branch; open PR with **exactly one** `Task: #N` and `Plan: Fxx-ID` pair, matching branch and trusted registry.
6. An independent Write/Admin reviewer who is not the PR author or commit author/committer must approve the **current revision**; applicable real CI and dependency/readiness checks must pass. Failing/absent/skipped critical checks block.
7. Merge to approved accepted integration branch `main` only after review, required checks and applicable project-owner authorization; do not automatically merge, force-push, rewrite history or bypass branch policy.
8. Developer submits the exact final pushed SHA, branch, real report, verification and publication confirmation. Orchestrator validates G0–G8, accepts once by (task ID, commit SHA), then and only then advances rotation.

**Bootstrap exception:** PR #38 is *pre-Genesis work*, not Cafer's rotation turn. It requires independent review and a separate explicit owner merge decision. Do not clear live issue assignees until the replacement governance gate and migration procedure are independently accepted.

Only the governance policy may update the task registry/dependencies and safety gates after independent review. All 31 technical tasks and 54 native prerequisites are retained, fixed owner/support/reviewer assignments removed in the proposed registry. See [TR SRS](docs/SRS.md), [EN SRS](docs/SRS_EN.md), [team guide](docs/TEAM_WORKFLOW.md), [dependency policy](docs/DEPENDENCY_MANAGEMENT.md), [security](SECURITY.md), [roadmap](docs/DEVELOPMENT_ROADMAP.md).

Do not infer product build/test success from governance test output. Always keep user V0 and frozen tests immutable.
