# Project Genesis v2.0 — Developer Team Operating Guide

**Owner-approved:** 2026-10-26. Five authorized developers in the fixed order:
**Burkay (@cakarburkayy) → Cafer (@caferkilinc) → Alperen Enes Yaman (@Yaman-A-E) → İsmail (@ismail-cevik) → Taha Uğur Toyran (@tahaugurtoyran) → repeat.**

## 1. What remains authoritative
- Product behavior: owner-provided Master Architecture v2.0 + Step-by-Step Development Guide v2.0; compiled [TR SRS](SRS.md) and [EN SRS](SRS_EN.md) await final sign-off.
- Existing implementation planning: [roadmap](DEVELOPMENT_ROADMAP.md), `.github/task-plan.json`, native GitHub prerequisites (31 technical issues and 54 edges).
- Execution model: PROJECT GENESIS v2.0. Exactly **one** authorized implementation owner at any point. Old module expertise and historical issue assignees are not permission to implement.
- Integration branch: `main`; issue-numbered topic branches and PRs remain for independent review, but do not permit several concurrent active writers.

## 2. Bootstrap migration safety
Existing [PR #38](https://github.com/caferkilinc/refactoring-ai-generated-code/pull/38) was prepared before Genesis. It does **not** consume a Burkay/Cafer rotation turn and is not a completed handoff. The project owner authorized reconciling it to Genesis, but did **not** authorize merging it. The active reviewer must inspect the current revision and actual CI; the owner will be asked for a **separate explicit merge decision**. Never bypass existing governance checks to force the transition.

The 31 native technical issues and their dependency graph are not deleted. Fixed assignees and legacy issue body primary/support/reviewer lines are cleared **only after** the new fail-closed gate, its regression tests and migration procedure have been accepted. The migration must preserve task IDs, issue links, Git history, budgets and known blockages.

## 3. One task per rotation
1. Orchestrator reconstructs last confirmed Git state, approved SRS, outstanding requirements and dependencies.
2. Orchestrator selects one READY technical task and issues one Codex contract with TASK_ID, MILESTONE, OWNER, expected baseline/branch, IN_SCOPE, OUT_OF_SCOPE, acceptance, verification and stop conditions.
3. Developer confirms local root, HEAD, worktree, upstream and expected accepted commit. Fetch and `git pull --ff-only` only after verifying safety.
4. Codex loads targeted SRS, architecture and source files; implements only the task; runs appropriate real checks; self-reviews diff and updates a concise `report.md`. No Codex commit/push without separate authorization.
5. Developer reviews, commits and pushes the numbered topic branch and opens PR linked to the assigned task. Independent current-commit reviewer (not author or committer) and genuine required CI checks remain mandatory; no auto-merge.
6. After human approval and explicit required merge authorization, PR changes reach accepted `main`. Developer sends `report.md`, correct task/owner, pushed commit and publication evidence.
7. Orchestrator evaluates G0–G8. It advances the rotation **once only** on ACCEPTED; otherwise retains owner and assigns scoped rework. Duplicate task+commit is idempotent.

A draft, push alone, passed governance tests or a project card marked Done is not sufficient evidence of accepted implementation. Never claim model/runtime/test success without actual output.

## 4. Repo safety and repeatable checks
Do not use destructive reset, clean, force-push, arbitrary local change discard, unaudited secret commits or premature paid API access. Maintain immutable V0 and frozen tests, isolated validation and two separate product approval gates. Existing governance checks on an eligible checkout:

```sh
python3 -m unittest discover -s tests/governance -v
python3 scripts/governance/check_docs.py
python3 scripts/governance/security_check.py
```

On Windows the equivalent interpreter entry point may be `py -3`. These commands test **governance only**; application build/test commands must be discovered from real manifests/CI after environment task #10.

## 5. Report and artifact reuse
Use `AGENTS.md` only for stable instructions and `.agents/skills/development-handoff/SKILL.md` when supported. Reuse `docs/PROJECT_STATUS.md` as the human-readable project-state snapshot and `docs/DEVELOPMENT_ROADMAP.md` as the canonical roadmap: do not create competing files. Detailed history stays in Git and material decisions in `docs/DECISIONS/`.

Before publication, `report.md` contains base commit and `PENDING_PUSH_CONFIRMATION`, not the SHA of its own commit. The resulting SHA is provided after push and accepted in a later verified handoff. Each developer hands off with real checks and blocking issues, then stops.

## 6. No artificial schedule certainty
The due date is **2027-01-01** (time UNKNOWN). Falcon-Mamba 7B, Python and JS/TS capabilities, PDF/HTML and mixed-language tests are first-delivery **P0**; lack of GPU/runtime/provider access is a release blocker, not approval to silently downgrade scope. Replan from evidence and actual available capacity, never from a speculative workload split.
