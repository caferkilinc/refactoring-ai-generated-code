# Secure Refactoring of AI-Generated Code

Engineering Design II — Ankara Bilim University. A planned multilingual platform for improving AI-generated code with controlled patches, reproducible analysis, isolated validation and two explicit product approvals.

**Current state (2026-10-22):** September planning/scaffolding history is preserved. Application modules, backend/frontend executable tests and experimental results are not implemented on `main`. Governance configuration is proposed in a review branch. See [actual status](docs/PROJECT_STATUS.md).

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

First-delivery P0: Java, Python, JavaScript and TypeScript (including mixed projects), real local Falcon-Mamba 7B, deterministic security, immutable V0, both user approvals, bounded real-provider refactoring, isolated candidate and combined verification, final ZIP, evidence-based HTML/PDF reports and history. C#/Go/C++ remain future scope. Lack of required GPU/provider access blocks release rather than becoming a fabricated PASS.

FastAPI/Redis/workers/storage and React/TypeScript/Monaco are planned components. No completed platform or measured improvement rate is claimed here. M3/macOS is a development environment; CUDA inference needs a separately verified GPU runtime.

## Working together

Start with [CONTRIBUTING](CONTRIBUTING.md) and [team workflow](docs/TEAM_WORKFLOW.md). Exactly one orchestrator-authorized developer may implement the dependency-ready task. Numbered topic PR branches remain for independent review, with `main` as accepted integration branch. PR #38 is a pre-Genesis bootstrap and requires separate owner merge approval. Private academic DOCX, raw user uploads and credentials stay outside this public repository.

- [Project board](https://github.com/users/caferkilinc/projects/1)
- [SRS Türkçe](docs/SRS.md) and [SRS English](docs/SRS_EN.md) (review drafts)
- [Architecture](docs/ARCHITECTURE.md) and [decisions](docs/DECISIONS/0001-scope-and-governance.md)
- [Roadmap and all 31 tasks](docs/DEVELOPMENT_ROADMAP.md)
- [Dependencies and gate](docs/DEPENDENCY_MANAGEMENT.md)
- [Weekly effort model](docs/TEAM_WORKLOAD.md)
- [Setup verification and remaining activation](docs/SETUP_REPORT.md)
- [Operational risks, fixes and remaining controls](docs/OPERATIONAL_AUDIT.md)

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
