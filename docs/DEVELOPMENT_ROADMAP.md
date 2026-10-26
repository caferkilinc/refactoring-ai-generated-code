# Genesis v2.0 transition and mandatory release scope

Owner decision (2026-10-26): 31 existing technical issues and 54 original dependencies are preserved, but fixed implementation assignments are removed. Java, Python, JavaScript, TypeScript, Falcon-Mamba 7B, mixed projects and evidence-linked HTML/PDF are all first-delivery **P0**. Historical estimates below are not current staffing commitments; the single active developer follows Burkay → Cafer → Alperen Enes Yaman → İsmail → Taha Uğur Toyran. PR #38 is a pre-Genesis bootstrap; merge requires independent review and an additional explicit project owner approval. See [TR SRS](SRS.md) and [EN SRS](SRS_EN.md).

# Development Roadmap — PROJECT GENESIS v2.0

**Status:** proposed staged migration; no Genesis handoff accepted yet. **Last update:** 2026-10-26. **Due:** 2027-01-01; exact time UNKNOWN.

## Authority and ordering

Technical source: owner-supplied Master Architecture v2.0 and Step-by-Step Development Guide v2.0, [Turkish SRS](SRS.md), [English SRS](SRS_EN.md). Execution source: PROJECT GENESIS v2.0. Previous 31 task IDs and 54 native prerequisite edges are retained. Old date windows are preliminary, NOT binding allocations and NOT proof that all mandatory scope fits before the deadline.

Only ONE active implementation developer at a time: Burkay → Cafer → Alperen Enes Yaman → İsmail → Taha Uğur Toyran → repeat. Do not treat issue assignee, epic historical role or model expertise as task authorization. Orchestrator selects one ready task from verified state and hard prerequisites; current execution state is in `.github/task-plan.json#sequential_execution` and [project status](PROJECT_STATUS.md). The canonical source for dependencies is the task registry and GitHub native issue edges.

**Scope elevation approved 2026-10-26:** Falcon-Mamba 7B (#19–#20), full PDF reports (#31), Python (#32), JavaScript/TypeScript (#33) and mixed language (#34) are first-delivery **P0** obligations. P1-only historical scheduling cannot defer them. C#/Go/C++ remain later extensions. P0 may be implemented in dependency order, not concurrently. No unapproved scope change.

## Six research work packages (not developer assignments)

| Package | Focus | GitHub issue |
|---|---|---|
| İP1 | One owner via rotation | #2 |
| İP2 | One owner via rotation | #3 |
| İP3 | One owner via rotation | #4 |
| İP4 | One owner via rotation | #5 |
| İP5 | One owner via rotation | #6 |
| İP6 | One owner via rotation | #7 |

## Retained technical tasks and dependencies

| Plan ID | Issue | Priority | Objective | Required task predecessors | Status |
|---|---:|---|---|---|---|
| F00-PLAN | #8 | P0 | Freeze scope, evidence protocol and resource decisions | None | IN PROGRESS |
| F00-V0 | #9 | P0 | Prepare working Java pilot and immutable experiment baseline | F00-PLAN | NOT STARTED |
| F01-GOV | #1 | P0 | Establish team workflow, dependency gate and project controls | None | IN PROGRESS |
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
| F14-MIX | #34 | P0 | Validate mixed-language capability integration | F14-PY, F14-JSTS | NOT STARTED |
| F15-P0 | #35 | P0 | Run P0 end-to-end acceptance and regression matrix | F13-BASIC | NOT STARTED |
| F15-EXPERIMENT | #36 | P0 | Evaluate refactoring tasks and sequential versus parallel execution | F15-P0, F00-PLAN | NOT STARTED |
| F15-HANDIN | #37 | P0 | Package reproducible release and academic delivery | F15-P0, F15-EXPERIMENT | NOT STARTED |

## Milestone acceptance, not calendar completion

- **F00–F03:** Approved requirements and V0, reproducible environment, typed contracts, stable job state and safe input.
- **F04–F07B:** Real Java parser/quality/baseline/sandbox, deterministic security, Falcon-Mamba 7B measured local reviewer.
- **F08–F12:** Two user approvals, context and conflicts, real bounded cloud patch, independent and combined validation.
- **F13–F14:** Before/after dashboard, full HTML/PDF/history, verified Python/JS/TS and mixed-component capabilities.
- **F15:** Java and multi-language E2E, frozen failure-inclusive experiment, reproducible first delivery and release review.

Every milestone requires actual task output, focused and integration verification, inspected acceptance evidence and accepted handoff. GitHub CI for governance does not prove product implementation.

## Current transition and release risks

1. Bootstrap PR #38 remains open and must be independently reviewed and owner-authorized to merge.
2. Fixed assignees in live GitHub issues are historic/transition metadata; removal must be coordinated only after compatible gate and review policy is accepted, without issue or dependency deletion.
3. SRS in Turkish/English is a draft pending a distinct final owner approval.
4. Actual local Falcon-Mamba GPU/runtime and real patch-provider API/consent/budget are not verified.
5. New mandatory P0 scope may exceed the remaining capacity; schedule feasibility must be reassessed, not disguised by inaccurate progress percentages.

**Next eligible development rotation:** Burkay, starting from no Genesis handoff. The task selected in `sequential_execution` is `F00-PLAN` (issue #8), conditional on successful bootstrap governance migration and accepted owner/SRS requirements. Its acceptance cannot be implied by this draft roadmap.
