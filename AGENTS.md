# Repository Codex instructions — Project Genesis v2.0

Project: secure refactoring of AI-generated code (Java, Python, JS/TS, local Falcon-Mamba 7B); preserve owner-approved Master Architecture v2.0 and Step-by-Step Development Guide v2.0.

## Source hierarchy
1. Explicit owner decisions (2026-10-26): `main` is accepted integration branch, PR #38 cannot merge without separate owner approval, all #19/#20/#31/#32/#33/#34 are first-delivery P0.
2. SRS: `docs/SRS.md` and `docs/SRS_EN.md` (both DRAFT pending separate final sign-off); do not silently treat drafts as accepted where requirements conflict.
3. Architecture: `docs/ARCHITECTURE.md` plus owner-provided v2.0 primary source PDFs (not assumed present in public repository).
4. Planning and actual state: `.github/task-plan.json`, `docs/DEVELOPMENT_ROADMAP.md`, `docs/PROJECT_STATUS.md`, `docs/DECISIONS/`, `.github/acceptance.json`; actual repository and tests establish IMPLEMENTED versus VERIFIED.
5. See `docs/TEAM_WORKFLOW.md`, `SECURITY.md`, `CONTRIBUTING.md`, `docs/DEPENDENCY_MANAGEMENT.md` for applicable detailed practice.

## Stable execution invariants
- Exactly one active implementation developer, cyclic order **Burkay → Cafer → Alperen Enes Yaman → İsmail → Taha Uğur Toyran → Burkay**. The orchestrator authorizes each task, accepts each evidence-backed handoff and advances at most once. Old issue assignments are transitional metadata, not valid owner authority.
- Do not modify source unless a bounded authorized task specifies its owner, ID, scope, dependencies, approved baseline, acceptance, verification and stop conditions. No next-task implementation after reporting.
- Before edits: identify root, clean/dirty worktree, HEAD, branch, remote/upstream and last accepted commit; stop on unsafe divergence or unexpected changes. Do not force push, reset --hard, clean, discard existing work or assume a PR is already merged.
- No unapproved architecture changes, extra infrastructure, speculative dependencies, unrelated refactors, test inflation, credentials, production secrets or unattended deployment.
- Honor immutable V0 and frozen test hashes. A successful build is not proof of behavioral preservation. Validate candidates individually and final combination, retaining separate behavioral and quality results. Do not weaken tests or leak secrets to models, logs or reports.
- Use actual repository-supported commands, record PASS/FAIL/NOT_RUN honestly; after two unproductive repair guesses without new evidence, stop and escalate.
- Prepare `report.md` as an active authorized task snapshot (no self-referential final commit SHA) and stop; human developer reviews/commits/pushes, then submits final SHA and report. Never claim publication before observed evidence.
- For authorized implementation or repair use `.agents/skills/development-handoff/SKILL.md` when installed/supported; otherwise follow an equivalent concise contract. Load only task-relevant context.

## PR #38 transition lock
This existing PR predates Project Genesis v2.0 and must undergo independent review and current CI first, then the owner's *separate explicit merge authorization*. Work on this preparatory branch is not a successful developer rotation. Do not clear old live issue assignments or merge the current migration before compatible governance gates and approval.
