# Secure Refactoring of AI-Generated Code

Engineering Design II — Ankara Bilim University. A planned multilingual platform for improving AI-generated code with controlled patches, reproducible analysis, isolated validation and two explicit product approvals.

**Current state (2026-10-27):** PR #38 and #39 are merged; SRS v0.4 TR/EN and 34-task/69-edge GitHub prerequisite graph are approved and audited. Application backend/frontend and product tests are still NOT_STARTED. See [actual status](docs/PROJECT_STATUS.md).

**Final course deadline: 2027-01-01; time unspecified.** All owner-approved Python/JS/TS, Falcon-Mamba, HTML/PDF and core refactoring capabilities are mandatory first-delivery P0; historical P1 schedule must be replanned. TÜBİTAK eligibility/application and advisors are separate, unverified decisions.

| Member | GitHub | Domain expertise (not fixed implementation assignment) |
|---|---|---|
| Cafer Tayyar Kılınç | @caferkilinc | Team Leader, FastAPI orchestrator, contracts, storage, integration |
| İsmail Çevik | @ismail-cevik | Sandbox, baseline tests, candidate/combined validation, QA |
| Alperen Enes Yaman | @Yaman-A-E | Local AI, context/conflict DAG, parallel refactoring, providers/retry |
| Burkay Çakar | @cakarburkayy | Language adapters, quality and deterministic security analysis |
| Taha Uğur Toyran | @tahaugurtoyran | Frontend, approval/diff screens, reporting/history, delivery demo |

All five repository accounts were verified on October 22: Cafer Admin, four collaborators Write.

## Scope

First-delivery P0: Java, Python, JavaScript, TypeScript, C#, Go and C++ (including mixed projects), real local Falcon-Mamba 7B, deterministic security, immutable V0, both user approvals, bounded real-provider refactoring, isolated candidate and combined verification, final ZIP, evidence-based HTML/PDF reports and history. C#/Go/C++ are also mandatory P0 first-delivery requirements per the owner decision on 2026-10-27, requiring real build/test/coverage/patch evidence. Lack of required GPU/provider access blocks release rather than becoming a fabricated PASS.

FastAPI/Redis/workers/storage and React/TypeScript/Monaco are planned components. No completed platform or measured improvement rate is claimed here. M3/macOS is a development environment; CUDA inference needs a separately verified GPU runtime.

## Working together

Start with [CONTRIBUTING](CONTRIBUTING.md) and [team workflow](docs/TEAM_WORKFLOW.md). Exactly one orchestrator-authorized developer may implement the dependency-ready task. Numbered topic branches remain for scoped review, with `main` as integration branch. Burkay is the sole required final approver; peer reviews are optional. PR #38 and #39 are already merged. Private academic DOCX, raw user uploads and credentials stay outside this public repository.

- [Project board](https://github.com/users/caferkilinc/projects/1)
- [SRS Türkçe](docs/SRS.md) and [SRS English](docs/SRS_EN.md) (both owner-approved v0.4)
- [Architecture](docs/ARCHITECTURE.md) and [decisions](docs/DECISIONS/0001-scope-and-governance.md)
- [Roadmap and all 34 tasks](docs/DEVELOPMENT_ROADMAP.md)
- [Dependencies and gate](docs/DEPENDENCY_MANAGEMENT.md)
- [Weekly effort model](docs/TEAM_WORKLOAD.md)
- [Developer environment and readiness](docs/DEVELOPMENT_ENVIRONMENT.md)

Governance verification (Python standard library, no dependencies):

```sh
python3 -m unittest discover -s tests/governance -v
python3 scripts/governance/check_docs.py
python3 scripts/governance/security_check.py
```

These checks validate development infrastructure. They do not demonstrate product validation or research experiment success.


## Current approved architecture and development state (2026-10-26)

The owner-approved target is the v2.0 modular secure-refactoring pipeline, including immutable V0, per-language analysis, deterministic security + local Falcon-Mamba 7B, two user approval gates, bounded context/LLM patching, individual and combined validation, Python/JS/TS, and measured ZIP/HTML/PDF/history. **This repository has not yet proven these product capabilities are implemented.** See [TR SRS](docs/SRS.md), [EN SRS](docs/SRS_EN.md), [architecture](docs/ARCHITECTURE.md), and [roadmap](docs/DEVELOPMENT_ROADMAP.md).

Implementation ownership rotates one at a time: **Burkay → Cafer → Alperen Enes Yaman → İsmail → Taha Uğur Toyran → repeat**, after evidence-based handoff acceptance. PR #38 predates this policy and cannot be counted as a rotation. `main` is the accepted integration branch; topic PR review remains mandatory. Current open PR #38 needs a separate owner merge authorization. The first delivery scope includes Falcon-Mamba, Python/JS/TS and full reporting; model hardware/provider capability is not yet verified.

**2026-10-27 change note:** See [TR SRS v0.4](docs/SRS.md), [EN SRS v0.4](docs/SRS_EN.md) and [roadmap](docs/DEVELOPMENT_ROADMAP.md). 34 planned tasks and 69 planned edges replace the old 31-task *planning total*, but the 31 original issues and 54 live native edges have been preserved. New GitHub native issue edges remain pending, not verified. No PR #38 merge authorization has been granted.

### Approval authority, 2026-10-27
Project owner Burkay Çakar alone provides required final authorization across development phases and merge decisions. Peer reviewer approvals are not required. A current-HEAD owner approval comment and actual task-appropriate CI remain mandatory for future task acceptance. PR #38 was owner-approved and merged as pre-Genesis work; PR #39 prepares seven-language planning on top of that foundation.
