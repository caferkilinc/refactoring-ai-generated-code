# ADR 0003 — Seven required first-delivery language adapters

**Status:** APPROVED SCOPE / IMPLEMENTATION NOT VERIFIED
**Owner decision date:** 2026-10-27
**Applies to:** Project Genesis v2.0; SRS v0.4 Turkish and English; F14/F15 planning; 2027-01-01 first-delivery target.

## Decision

The first delivery requires **working Java, Python, JavaScript, TypeScript, C#, Go and C++ language adapters**, plus real Falcon-Mamba 7B and all previously approved product capabilities. Historical classifications of C#/Go/C++ as future scope are superseded. No incomplete language integration may be reported as a completed mandatory release.

## Planned engineering implementation

- `F14-CS` GitHub issue #40: Roslyn/.NET AST, symbols, quality, real build/test/coverage and safe patch validation.
- `F14-GO` issue #41: Go AST/types/modules, real quality/test/coverage and safe patch validation.
- `F14-CPP` issue #42: Clang AST/includes/compilation database, real native build/test/coverage and safe patch validation.
- Each new adapter depends on `F02-CONTRACT`, `F06-SANDBOX` and `F11-VALIDATE`.
- `F14-MIX` now requires existing Python + JS/TS adapters and **all three** new adapters; `F15-P0` requires `F14-MIX`, `F07B-LOCAL` and `F13-ADV` in addition to earlier requirements.
- Keep all original 31 tasks and all 54 original native GitHub edges. Three new issue records and 15 planned edges create a **34-task/69-edge proposed DAG**. Newly required native GitHub links are not established by changing a JSON file and remain `PENDING_SAFE_SYNC`.

## Acceptance evidence and safety

Acceptance requires real positive and negative fixture runs per language, persisted source/tool/version evidence, baseline-frozen tests, no unsafe host execution, correct per-component coverage, guarded patch/revalidation and seven-language final user workflow. Unavailable SDK/compiler, missing build context or GPU/provider service must be recorded as blocked/unverified, not passing. The expanded scope increases schedule risk under single-owner rotation: do not guarantee the 2027-01-01 date without an evidence-based resource and critical-path reforecast.

## Governance impact

PR #38 and PR #39 remain subject to independent current-head review, required checks and explicit **separate owner approval before PR #38 is merged**. PR #38 is pre-Genesis and does not advance the Burkay → Cafer → Alperen → İsmail → Uğur sequence. Approved scope is distinct from final sign-off of the bilingual SRS texts, which is still pending.
