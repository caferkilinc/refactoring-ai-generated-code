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

Start with [CONTRIBUTING](CONTRIBUTING.md), [team workflow](docs/TEAM_WORKFLOW.md) and the [Codex-native protocol and activation conditions](docs/governance/PROJECT_GENESIS_CODEX_NATIVE_PROTOCOL_V3.md). One authorized developer implements the registered task on a numbered topic branch. `main` is the integration branch. Private academic DOCX, raw user uploads and credentials stay outside this public repository.

- [Project board](https://github.com/users/caferkilinc/projects/1)
- [SRS Türkçe](docs/SRS.md) and [SRS English](docs/SRS_EN.md) (both owner-approved v0.4)
- [Architecture](docs/ARCHITECTURE.md) and [decisions](docs/DECISIONS/0001-scope-and-governance.md)
- [Roadmap and all 34 tasks](docs/DEVELOPMENT_ROADMAP.md)
- [Dependencies and gate](docs/DEPENDENCY_MANAGEMENT.md)
- [Weekly effort model](docs/TEAM_WORKLOAD.md)
- [Developer preflight and development workflow](docs/TEAM_WORKFLOW.md)

Governance verification (Python standard library, no dependencies):

```sh
python3 -m unittest discover -s tests/governance -v
python3 scripts/governance/check_docs.py
python3 scripts/governance/security_check.py
```

These checks validate development infrastructure. They do not demonstrate product validation or research experiment success.


## Current approved architecture and development state (2026-10-26)

The owner-approved target is the v2.0 modular secure-refactoring pipeline, including immutable V0, per-language analysis, deterministic security + local Falcon-Mamba 7B, two user approval gates, bounded context/LLM patching, individual and combined validation, Python/JS/TS, and measured ZIP/HTML/PDF/history. **This repository has not yet proven these product capabilities are implemented.** See [TR SRS](docs/SRS.md), [EN SRS](docs/SRS_EN.md), [architecture](docs/ARCHITECTURE.md), and [roadmap](docs/DEVELOPMENT_ROADMAP.md).

Implementation ownership rotates one at a time: **Burkay → Cafer → Alperen Enes Yaman → İsmail → Taha Uğur Toyran → repeat**, after evidence-based handoff acceptance. PR #38 was merged as pre-Genesis work and consumed no rotation. `main` is the accepted integration branch and topic PR review remains mandatory. The first delivery scope includes Falcon-Mamba, Python/JS/TS and full reporting; model hardware/provider capability is not yet verified.

**2026-10-27 change note:** See [TR SRS v0.4](docs/SRS.md), [EN SRS v0.4](docs/SRS_EN.md) and [roadmap](docs/DEVELOPMENT_ROADMAP.md). The plan expanded to 34 tasks and 69 edges while preserving the 31 original issues and 54 original edges.

### Historical approval, 2026-10-27
The owner-only v2 decision and pre-Genesis PR #38 approval remain part of the [decision history](docs/DECISIONS/0004-sole-owner-approval.md). Follow the currently effective protocol for new work.
