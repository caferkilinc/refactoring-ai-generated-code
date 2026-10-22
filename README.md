# Secure Refactoring of AI-Generated Code

Engineering Design II — Ankara Bilim University. A planned multilingual platform for improving AI-generated code with controlled patches, reproducible analysis, isolated validation and two explicit product approvals.

**Current state (2026-10-22):** September planning/scaffolding history is preserved. Application modules, backend/frontend executable tests and experimental results are not implemented on `main`. Governance configuration is proposed in a review branch. See [actual status](docs/PROJECT_STATUS.md).

**Final course deadline: 2027-01-01; time unspecified.** P0 target December 13, P1 cutoff December 20, package December 27, reserve December 28–31. TÜBİTAK eligibility/application and advisors are separate, unverified decisions.

| Member | GitHub | Primary responsibility |
|---|---|---|
| Cafer Tayyar Kılınç | @caferkilinc | Team Leader, FastAPI orchestrator, contracts, storage, integration |
| İsmail Çevik | @ismail-cevik | Sandbox, baseline tests, candidate/combined validation, QA |
| Alperen Enes Yaman | @Yaman-A-E | Local AI, context/conflict DAG, parallel refactoring, providers/retry |
| Burkay Çakar | @cakarburkayy | Language adapters, quality and deterministic security analysis |
| Taha Uğur Toyran | @tahaugurtoyran | Frontend, approval/diff screens, reporting/history, delivery demo |

All five repository accounts were verified on October 22: Cafer Admin, four collaborators Write.

## Scope

P0: Java pilot → safe input/V0 → language and quality/security analysis → approval 1 → bounded dependency-aware parallel patches → candidate tests → approval 2 → combined validation → final ZIP/basic measured report. P1: real Local AI, Python/JavaScript/TypeScript, mixed projects and advanced reporting. Local AI does not block Java P0.

FastAPI/Redis/workers/storage and React/TypeScript/Monaco are planned components. No completed platform or measured improvement rate is claimed here. M3/macOS is a development environment; CUDA inference needs a separately verified GPU runtime.

## Working together

Start with [CONTRIBUTING](CONTRIBUTING.md) and [team workflow](docs/TEAM_WORKFLOW.md). Choose an existing issue and numbered topic branch; submit a PR, obtain independent review and evidence-backed acceptance. Private academic DOCX, raw user uploads and credentials stay outside this public repository.

- [Project board](https://github.com/users/caferkilinc/projects/1)
- [Architecture](docs/ARCHITECTURE.md) and [decisions](docs/DECISIONS/0001-scope-and-governance.md)
- [Roadmap and all 31 tasks](docs/DEVELOPMENT_ROADMAP.md)
- [Dependencies and gate](docs/DEPENDENCY_MANAGEMENT.md)
- [Weekly effort model](docs/TEAM_WORKLOAD.md)
- [Setup verification and remaining activation](docs/SETUP_REPORT.md)

Governance verification (Python standard library, no dependencies):

```sh
python3 -m unittest discover -s tests/governance -v
python3 scripts/governance/check_docs.py
python3 scripts/governance/security_check.py
```

These checks validate development infrastructure. They do not demonstrate product validation or research experiment success.
