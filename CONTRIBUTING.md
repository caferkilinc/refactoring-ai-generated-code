# Contribution procedure

1. Select the registered task and check its scope, contracts, mandatory dependencies, support and reviewer.
2. Fetch current `main`; create `feature/<issue>-slug`, `fix/<issue>-slug`, `docs/<issue>-slug`, `test/<issue>-slug` or `chore/<issue>-slug`.
3. Develop and run relevant real checks. Contract fixtures permit parallel development before integrated dependencies are complete.
4. Make a descriptive Conventional Commit (`feat:`, `fix:`, `docs:`, `test:`, `chore:`); push the topic branch.
5. Open a PR with exactly one `Task: #N` and `Plan: Fxx-ID` line, matching the branch and trusted registry.
6. Resolve review comments and checks. At least one independent reviewer must approve the current revision.
7. Merge only after maintainer approval and acceptance. Do not directly push `main`, force push, or erase history.
8. Record evidence and accepted merged PR in the reviewed main acceptance registry; update the task/project only after acceptance.

New bugs/features must first be registered in `.github/task-plan.json` through a reviewed governance PR; PR text cannot invent a new task, scope or dependency bypass. See [gate policy](docs/DEPENDENCY_MANAGEMENT.md).

Until protection is explicitly activated, this is a documented procedure rather than a technical merge restriction. The bootstrap PR is reviewed manually because trusted base `main` does not yet contain its own gate.

See [Mac/Windows commands](docs/TEAM_WORKFLOW.md), [security policy](SECURITY.md) and the [roadmap](docs/DEVELOPMENT_ROADMAP.md). Research/documentation tasks use appropriate evidence instead of fabricated executable test results.
