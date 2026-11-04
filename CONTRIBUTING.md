# Contribution workflow — Project Genesis

Use the [canonical execution policy](docs/governance/PROJECT_GENESIS_CODEX_NATIVE_PROTOCOL_V3.md) and its activation conditions. The trusted task registry identifies **one** current developer and task in the fixed rotation. Use a bounded task contract with Plan ID, GitHub issue, accepted baseline, scope and acceptance checks.

1. Verify canonical `main`, active developer, registered task, and accepted prerequisites. Under active v3 the developer explicitly authorizes Codex to execute that task.
2. Authorized developer checks local worktree/HEAD/upstream/remote; safely syncs `main` (only clean and fast-forward when appropriate).
3. Use issue-numbered topic branch (`feature/<issue>-slug`, `fix/<issue>-slug`, `docs/<issue>-slug`, `test/<issue>-slug`, `chore/<issue>-slug`) for independent PR review. Only the current owner implements; the existence of a topic branch does not create concurrent authorization.
4. Implement the bounded task, run real task-specific checks, review scope/secrets, produce a concise `report.md` with `PENDING_PUSH_CONFIRMATION`. Codex MUST stop after one task and cannot claim push/merge.
5. Human reviews and publishes to topic branch; open PR with **exactly one** `Task: #N` and `Plan: Fxx-ID` pair, matching branch and trusted registry.
6. Under active v3 the developer records authenticated, exact-head merge approval. Protected changes require separate project-owner authorization. Satisfy independent GitHub reviews required by hosted settings and all applicable CI, dependency and readiness checks.
7. Merge to `main` only with explicit authorization and verified hosted protections. Keep publication, merge, and acceptance evidence separate.
8. Submit the exact final source SHA, branch, report, verification and publication proof for independent acceptance. Update acceptance and rotation together only after review, once per task and source SHA.

**Historical bootstrap:** PR #38 was owner-authorized pre-Genesis work and consumed no rotation turn. Handle legacy issue assignee cleanup as separately authorized maintenance.

Only the governance policy may update the task registry/dependencies and safety gates after independent review. All 31 technical tasks and 54 native prerequisites are retained, fixed owner/support/reviewer assignments removed in the proposed registry. See [TR SRS](docs/SRS.md), [EN SRS](docs/SRS_EN.md), [team guide](docs/TEAM_WORKFLOW.md), [dependency policy](docs/DEPENDENCY_MANAGEMENT.md), [security](SECURITY.md), [roadmap](docs/DEVELOPMENT_ROADMAP.md).

Do not infer product build/test success from governance test output. Always keep user V0 and frozen tests immutable.
