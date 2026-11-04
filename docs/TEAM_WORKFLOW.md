# Project Genesis — Developer Team Operating Guide

> Follow the [Codex-native v3 protocol](governance/PROJECT_GENESIS_CODEX_NATIVE_PROTOCOL_V3.md) after its activation gates pass. Until then the [v2.1 protocol](governance/PROJECT_GENESIS_ORCHESTRATOR_PROTOCOL_V2_1.md) governs execution.

**Owner-approved:** 2026-10-26. Five authorized developers in the fixed order:
**Burkay (@cakarburkayy) → Cafer (@caferkilinc) → Alperen Enes Yaman (@Yaman-A-E) → İsmail (@ismail-cevik) → Taha Uğur Toyran (@tahaugurtoyran) → repeat.**

## 1. What remains authoritative
- Product behavior: owner-provided Master Architecture v2.0 + Step-by-Step Development Guide v2.0; [TR SRS](SRS.md) and [EN SRS](SRS_EN.md) v0.4.0 were approved by Burkay Çakar on 2026-10-27. Approval does not prove implementation.
- Existing implementation planning: [roadmap](DEVELOPMENT_ROADMAP.md), `.github/task-plan.json`, and the verified GitHub-native graph: 34 technical tasks / 69 dependencies (31 original tasks and 54 original edges preserved). Actual acceptances and the active owner come from the trusted registry and GitHub evidence, not legacy issue assignees.
- Execution model: exactly **one** authorized implementation owner at any point. Module expertise and historical issue assignees do not grant implementation authority.
- Integration branch: `main`; issue-numbered topic branches and PRs remain for independent review, but do not permit several concurrent active writers.

## 2. Bootstrap migration safety
Historical [PR #38](https://github.com/caferkilinc/refactoring-ai-generated-code/pull/38) was prepared before Genesis. The project owner authorized its merge on 2026-10-27 at `5754ed6eeaeef0cce9bc46264c8baeddfb62f88c`. It consumed no rotation turn.

The 31 original technical issues and their 54 native dependencies were preserved; 3 required language tasks (#40–#42) and 15 new dependency edges were added, bringing the audited live graph to 34 tasks / 69 edges. Legacy fixed-assignee cleanup is PARTIAL and must be handled only in separately authorized maintenance; do not erase historical work or the dependency graph.

## 3. One task per rotation
1. Pin live `main` and verify the trusted task registry, acceptance evidence and native prerequisites.
2. Under active v3 the registered developer authorizes one bounded contract with TASK_ID, OWNER, expected baseline/branch, IN_SCOPE, OUT_OF_SCOPE, acceptance, verification and stop conditions.
3. Developer confirms local root, HEAD, worktree, upstream and expected accepted commit. Fetch canonical refs and fast-forward clean `main` only when verified safe.
4. Codex loads targeted SRS, architecture and source files; implements only the task; runs appropriate real checks; self-reviews diff and updates a concise `report.md`. No Codex commit/push without separate authorization.
5. Developer reviews the diff and evidence. Under active v3, one explicit `PUSHLA` authorizes the eligible sequence for that review, with exact-head merge approval recorded under the active policy. Protected changes require separate project-owner authorization.
6. Verify hosted CI, required GitHub reviews and merge evidence. Deliver `report.md`, task, owner, source SHA and publication evidence.
7. Independently verify and record acceptance before proposing the next prompt. Advance **once only** per accepted task and source SHA.

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

## 7. Mandatory 2026-10-27 release scope
Every adapter for Java, Python, JavaScript, TypeScript, C#, Go and C++ is **P0**; real local Falcon-Mamba 7B, frozen V0/tests, isolated patch verification, two product approvals and HTML/PDF/ZIP/history remain mandatory. F14-MIX depends on all seven adapters, and F15-P0 requires the final integration gates. PR #38 and #39 are merged historical transitions. The [PR #45 delegation](DECISIONS/0006-pr45-revision-bound-delegation.md) remains tied to its accepted head.
