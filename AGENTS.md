# Repository Codex instructions — Project Genesis v2.0

Project: secure refactoring of AI-generated code (**Java, Python, JavaScript, TypeScript, C#, Go, C++ and local Falcon-Mamba 7B**, all P0 first-delivery); preserve owner-approved Master Architecture v2.0 and Step-by-Step Development Guide v2.0.

## Source hierarchy
1. Explicit owner decisions (2026-10-26 and 2026-10-27): `main` is accepted integration branch, PR #38 was explicitly owner-authorized and merged (2026-10-27), all #19/#20/#31/#32/#33/#34/#40/#41/#42 are first-delivery P0; verified seven-language acceptance is mandatory.
2. SRS: `docs/SRS.md` and `docs/SRS_EN.md` (both DRAFT pending separate final sign-off); do not silently treat drafts as accepted where requirements conflict.
3. Architecture: `docs/ARCHITECTURE.md` plus owner-provided v2.0 primary source PDFs (not assumed present in public repository).
4. Planning and actual state: `.github/task-plan.json`, `docs/DEVELOPMENT_ROADMAP.md`, `docs/PROJECT_STATUS.md`, `docs/DECISIONS/`, `.github/acceptance.json`; actual repository and tests establish IMPLEMENTED versus VERIFIED.
5. See approved scope record `docs/DECISIONS/0003-mandatory-seven-language-delivery.md`; see `docs/TEAM_WORKFLOW.md`, `SECURITY.md`, `CONTRIBUTING.md`, `docs/DEPENDENCY_MANAGEMENT.md` for applicable detailed practice.

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
PR #38 was merged into `main` on the owner's 2026-10-27 explicit authorization; it does not consume a rotation. Project owner Burkay alone approves each later PR and handoff; record `GENESIS-OWNER-APPROVED: <head SHA>` as an authenticated GitHub PR comment. Peer approvals are OPTIONAL, but real CI, task acceptance, safe publication and Git graph verification remain mandatory. Do not clear live issue assignments before approved governance is integrated and native dependencies match.

## First-delivery language acceptance
All seven language adapters require real symbol/quality/build/test/coverage and bounded validated patch evidence where applicable. F14-MIX depends on #32/#33/#40/#41/#42; F15-P0 also requires real local security AI and full PDF reporting. The 34-task/69-edge **planned** graph must not be mistaken for GitHub-native completion; original 31-task/54-edge graph is preserved and the new links remain pending reconciliation. Do not state release READY if a mandatory language, model, negative-path, or combined-test gate is unverified.
