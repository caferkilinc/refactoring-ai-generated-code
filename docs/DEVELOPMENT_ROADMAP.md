# Genesis v2.0 transition and mandatory release scope

Owner decision (2026-10-27): 31 existing technical issues and 54 original dependencies are retained, with three new unassigned P0 issues (#40–#42) and a staged 34-task / 69-edge dependency graph, but fixed implementation assignments are removed. Java, Python, JavaScript, TypeScript, Falcon-Mamba 7B, mixed projects and evidence-linked HTML/PDF are all first-delivery **P0**. Historical estimates below are not current staffing commitments; the single active developer follows Burkay → Cafer → Alperen Enes Yaman → İsmail → Taha Uğur Toyran. PR #38 is pre-Genesis bootstrap and was merged to `main` on Burkay Çakar's explicit approval (`5754ed6eeaeef0cce9bc46264c8baeddfb62f88c`). Burkay is the sole required approval authority; other reviewers are optional. See [TR SRS](SRS.md) and [EN SRS](SRS_EN.md).

# Development Roadmap — PROJECT GENESIS v2.0

**Status:** owner-approved implementation plan; sequential application NOT_STARTED, native graph sync pending; no Genesis handoff accepted yet. **Last update:** 2026-10-27. **Due:** 2027-01-01; exact time UNKNOWN.

## Authority and ordering

Technical source: owner-supplied Master Architecture v2.0 and Step-by-Step Development Guide v2.0, [Turkish SRS](SRS.md), [English SRS](SRS_EN.md). Execution source: PROJECT GENESIS v2.0. Original 31 task IDs and their 54 live native prerequisite edges are retained; the new 34-task plan has 69 intended edges, but new native relations are **PENDING_SAFE_SYNC** (not yet verified live). Old date windows are preliminary, NOT binding allocations and NOT proof that all mandatory scope fits before the deadline.

Only ONE active implementation developer at a time: Burkay → Cafer → Alperen Enes Yaman → İsmail → Taha Uğur Toyran → repeat. Do not treat issue assignee, epic historical role or model expertise as task authorization. Orchestrator selects one ready task from verified state and hard prerequisites; current execution state is in `.github/task-plan.json#sequential_execution` and [project status](PROJECT_STATUS.md). The canonical source for dependencies is the task registry and GitHub native issue edges.

**Scope elevation approved 2026-10-26:** Falcon-Mamba 7B (#19–#20), full PDF reports (#31), Python (#32), JavaScript/TypeScript (#33) and mixed language (#34) are first-delivery **P0** obligations. P1-only historical scheduling cannot defer them. C#, Go and C++ are mandatory first-delivery P0 under the 2026-10-27 owner decision. Each requires real adapter/source symbols, tests, coverage, safely validated patch E2E and release evidence. P0 may be implemented in dependency order, not concurrently. No unapproved scope change.

## Six research work packages (not developer assignments)

| Package | Focus | GitHub issue |
|---|---|---|
| İP1 | Experiment baseline and platform contracts | #2 |
| İP2 | Language adapters, initial quality and behavior measurement | #3 |
| İP3 | Deterministic security and mandatory Falcon-Mamba | #4 |
| İP4 | Approval 1, dependency-aware context and controlled patching | #5 |
| İP5 | Evidence-based validation, final version and reporting | #6 |
| İP6 | Mandatory multilingual expansion and empirical evaluation | #7 |

## Technical task registry and mandatory dependencies — revised 2026-10-27

**34 P0 tasks = 31 existing + 3 added (#40–#42).** The original 54 live native issue edges are preserved. The new 69-edge directed task plan has been recorded in `.github/task-plan.json`, but GitHub native issue parent/dependency updates **remain pending**; no downstream task may claim prerequisites accepted until that graph is reconciled.

| Plan ID | Issue | P | Scope | Prerequisite Plan IDs | Registry status |
|---|---:|---|---|---|---|
| F00-PLAN | #8 | P0 | Freeze scope, evidence protocol and resource decisions | — | IN PROGRESS |
| F00-V0 | #9 | P0 | Prepare working Java pilot and immutable experiment baseline | F00-PLAN | NOT STARTED |
| F01-GOV | #1 | P0 | Establish team workflow, dependency gate and project controls | — | IN PROGRESS |
| F01-ENV | #10 | P0 | Create reproducible development services and real application checks | F01-GOV | NOT STARTED |
| F02-CONTRACT | #11 | P0 | Approve CIR, LanguageAdapter and API contracts for parallel development | F00-PLAN | NOT STARTED |
| F02-STATE | #12 | P0 | Implement metadata, state machine, queue and idempotency | F02-CONTRACT, F01-ENV | NOT STARTED |
| F03-INPUT | #13 | P0 | Implement safe upload, consent and immutable artefacts | F02-STATE | NOT STARTED |
| F04-JAVA | #14 | P0 | Implement Language Router and Java symbol adapter | F02-CONTRACT, F03-INPUT | NOT STARTED |
| F05-QUALITY | #15 | P0 | Normalize real quality findings and comparable metrics | F04-JAVA | NOT STARTED |
| F06-SANDBOX | #16 | P0 | Build isolated worker execution with resource limits | F01-ENV, F03-INPUT | NOT STARTED |
| F06-TESTS | #17 | P0 | Freeze baseline tests and parse build/test/coverage evidence | F00-V0, F04-JAVA, F06-SANDBOX | NOT STARTED |
| F07A-SCAN | #18 | P0 | Integrate deterministic security scans and redaction | F05-QUALITY, F03-INPUT | NOT STARTED |
| F07B-PILOT | #19 | P0 | Verify GPU access, model variant and runtime compatibility | F00-PLAN | BLOCKED |
| F07B-LOCAL | #20 | P0 | Serve Local AI review and evaluate labelled security examples | F07B-PILOT, F07A-SCAN | NOT STARTED |
| F08-UI | #21 | P0 | Build first approval UI against approved API fixtures | F02-CONTRACT, F01-ENV | NOT STARTED |
| F08-INTEGRATE | #22 | P0 | Integrate real issue selection and approval snapshot | F08-UI, F05-QUALITY, F06-TESTS, F07A-SCAN | NOT STARTED |
| F09-CONTEXT | #23 | P0 | Build dependency-aware context and symbol/test references | F02-CONTRACT, F04-JAVA | NOT STARTED |
| F09-SCHED | #24 | P0 | Implement conflict DAG and bounded parallel scheduling | F09-CONTEXT | NOT STARTED |
| F10-PATCH | #25 | P0 | Implement real provider patch generation and scope guard | F03-INPUT, F08-INTEGRATE, F09-SCHED | BLOCKED |
| F11-VALIDATE | #26 | P0 | Implement candidate validation and dual result states | F06-TESTS, F10-PATCH, F07A-SCAN | NOT STARTED |
| F11-RETRY | #27 | P0 | Implement bounded retry with recorded feedback | F11-VALIDATE | NOT STARTED |
| F12-REVIEW | #28 | P0 | Implement diff review and second approval UI | F08-UI, F02-CONTRACT | NOT STARTED |
| F12-FINAL | #29 | P0 | Combine approved patches, revalidate and export final ZIP | F11-VALIDATE, F11-RETRY, F12-REVIEW | NOT STARTED |
| F13-BASIC | #30 | P0 | Report real before/after values and basic history | F12-FINAL, F05-QUALITY | NOT STARTED |
| F13-ADV | #31 | P0 | Add PDF and extended report/history presentation | F13-BASIC | NOT STARTED |
| F14-PY | #32 | P0 | Implement Python adapter without Java-specific assumptions | F13-BASIC, F04-JAVA | NOT STARTED |
| F14-JSTS | #33 | P0 | Implement JavaScript and TypeScript adapters | F13-BASIC, F04-JAVA | NOT STARTED |
| F14-MIX | #34 | P0 | Validate mixed-language capability integration | F14-PY, F14-JSTS, F14-CS, F14-GO, F14-CPP | NOT STARTED |
| F15-P0 | #35 | P0 | Run P0 end-to-end acceptance and regression matrix | F13-BASIC, F13-ADV, F07B-LOCAL, F14-MIX | NOT STARTED |
| F15-EXPERIMENT | #36 | P0 | Evaluate refactoring tasks and sequential versus parallel execution | F15-P0, F00-PLAN | NOT STARTED |
| F15-HANDIN | #37 | P0 | Package reproducible release and academic delivery | F15-P0, F15-EXPERIMENT | NOT STARTED |
| F14-CS | #40 | P0 | Implement verified C# / Roslyn language adapter | F02-CONTRACT, F06-SANDBOX, F11-VALIDATE | NOT STARTED |
| F14-GO | #41 | P0 | Implement verified Go language adapter | F02-CONTRACT, F06-SANDBOX, F11-VALIDATE | NOT STARTED |
| F14-CPP | #42 | P0 | Implement verified C++ / Clang language adapter | F02-CONTRACT, F06-SANDBOX, F11-VALIDATE | NOT STARTED |

**Added P0 work:** F14-CS/#40 Roslyn, F14-GO/#41 Go modules/types, F14-CPP/#42 Clang/native build. Each depends on F02-CONTRACT + F06-SANDBOX + F11-VALIDATE. **Release-critical joins:** F14-MIX/#34 waits for Python/JS/TS plus all three new adapters; F15-P0/#35 waits for F13-BASIC + F13-ADV + F07B-LOCAL + F14-MIX. The latter blocks the experiment and final hand-in through existing F15 dependencies.

**Important schedule constraint:** Several historic dates and effort estimates are infeasible to treat as confirmed after seven-language expansion and strictly sequential ownership. They remain archival planning values; a dependency-based reforecast and toolchain availability check are mandatory before confirming delivery feasibility.

## Milestone acceptance, not calendar completion

- **F00–F03:** Approved requirements and V0, reproducible environment, typed contracts, stable job state and safe input.
- **F04–F07B:** Real Java parser/quality/baseline/sandbox, deterministic security, Falcon-Mamba 7B measured local reviewer.
- **F08–F12:** Two user approvals, context and conflicts, real bounded cloud patch, independent and combined validation.
- **F13–F14:** Before/after dashboard, full HTML/PDF/history, verified Python/JS/TS/C#/Go/C++ and mixed-component capabilities.
- **F15:** E2E acceptance for all seven languages plus actual Falcon-Mamba, frozen failure-inclusive experiment, reproducible first delivery and release review.

Every milestone requires actual task output, focused and integration verification, inspected acceptance evidence and accepted handoff. GitHub CI for governance does not prove product implementation.

## Current transition and release risks

1. Bootstrap PR #38 remains open and must be independently reviewed and owner-authorized to merge.
2. Fixed assignees in live GitHub issues are historic/transition metadata; removal must be coordinated only after compatible gate and review policy is accepted, without issue or dependency deletion.
3. Both Turkish and English SRS v0.4 are explicitly approved by Burkay on 2026-10-27; do not confuse approval with verified software.
4. Actual local Falcon-Mamba GPU/runtime, C#/.NET, Go and C++/Clang toolchains, and patch-provider API/consent/budget are not verified.
5. New #40–#42 issues currently have no GitHub-native #7 parent or blocked_by edges; #34 and #35 still have their historical live predecessors. Sync safely after governance review; do not call the 69 planned edges live.
6. New mandatory P0 scope may exceed the remaining capacity; schedule feasibility must be reassessed, not disguised by inaccurate progress percentages.

**Next eligible development rotation:** Burkay, starting from no Genesis handoff. The task selected in `sequential_execution` is `F00-PLAN` (issue #8), conditional on successful bootstrap governance migration and accepted owner/SRS requirements. Its acceptance cannot be implied by this draft roadmap.

## Final planning acceptance (2026-10-27)

**Approved by:** Burkay Çakar. This roadmap defines all 34 mandatory implementation tasks across the existing six research work packages; every one is P0 and links to current functional/nonfunctional requirements. An audit of the task registry confirms **69 unique, valid directed prerequisite edges, zero missing task references, and no dependency cycle**. All 31 original issues and 54 original live edges are preserved. Exactly 15 new live prerequisite edges and three parent links remain subject to the gated graph synchronization and post-write audit. Start with active F00-PLAN (#8), owner Burkay. F01-GOV (#1) is pre-Genesis governance work, not a completed rotation or authorization to skip F00-PLAN. No second owner begins without accepted handoff.

**Planning capacity warning:** Current registry estimates sum to **436–666 person-hours** for the 34 tasks. These are historical/rough planning figures, NOT actual executed hours and NOT a credible 2027-01-01 completion forecast without staffing and runtime evidence. The one-active-owner rule prohibits parallel implementation; prioritize mandatory prerequisites and reforecast after the real baseline. No mandatory adapter, Falcon-Mamba, negative-path validation or final report can be silently deferred. The next Codex prompt is intentionally NOT generated by this plan-acceptance phase.

**Sole approval control:** Burkay posts `GENESIS-OWNER-APPROVED: <CURRENT_HEAD_SHA>` in the relevant PR conversation. Peer approvals are optional; checks, Git ancestry, immutable V0 and product acceptance still apply. Implementation readiness and release readiness remain `NOT_READY` until demonstrated.
