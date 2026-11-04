# F02 requirements to deliverables

Product authorities: approved [TR SRS](../SRS.md), [EN SRS](../SRS_EN.md),
[architecture](../ARCHITECTURE.md), [ADR 0003](../DECISIONS/0003-mandatory-seven-language-delivery.md),
[ADR 0005](../DECISIONS/0005-f00-research-baseline.md) and registered F02-CONTRACT
Issue #11. Private Master Architecture v2.0 / development-guide source PDFs are
not available in this workspace and their contents were not fabricated.

| Requirement | Contract / semantics | Consumer | Verification | Allowed output |
|---|---|---|---|---|
| FR-007 | Nine versioned CIR entities and one shared model registry | All | Positive mandatory-entity examples, independent schema validation, export consistency | backend/core/schemas/, tests/contracts/, docs/contracts/ |
| FR-010–014, FR-023–024; Q05/Q09/Q10 | Source identity/ranges, symbols, dependency edges, rules/tools/evidence and stable scope | UI, adapter | Unicode/tab/CRLF bounds, invalid paths/ranges, broken/wrong-kind/duplicate IDs, scope mismatches | Same three directories |
| FR-011, FR-058–062; NFR-14 | Seven languages, nine independent capability dimensions and explicit unavailable/unimplemented states | Adapter | Seven-language fixture and actual guard normal/error cases | Same three directories |
| FR-015–017, FR-054–056; NFR-03/05/11 | Security classification, model provenance, UNCONFIRMED LLM claims, redaction states and safe errors | UI, security/context | Security-only selection rejection, missing scans, LLM verification and credential-field rejection | Same three directories |
| FR-020–022, FR-025–026 | Frozen suite/test references and immutable Gate 1 selection | UI, context | Passing nonempty baseline required; stale snapshot/version and replaced suite rejected | Same three directories |
| FR-027–030 | Bounded reference-only ContextPackage, side effects, public APIs, unresolved/missing context and budgets | Context/refactoring | Complete/incomplete and broken-reference/call-edge/redaction constraints | Same three directories |
| FR-031–036; NFR-02 | Patch provenance, diff/output hashes, trusted path/file/suite policy, attempts and separate outcome dimensions | Refactoring/validation | Frozen/test/symlink/out-of-scope/forged flags, snapshot-matched tests/scans, quality pairs and failed denominator cases | Same three directories |
| FR-035, FR-039–043; NFR-04/10/12 | Independent behavior/quality/security/execution and candidate/combined workspaces, comparable metric units | UI/validation/reporting | PASSED+IMPROVED/UNCHANGED/WORSE and UNVERIFIED+NOT_COMPARABLE; zero/nonmeasured/count/currency and combined-workspace checks | Same three directories |
| NFR-07; Q07/Q08/Q11/Q18 | JSON Schema 2020-12, OpenAPI 3.1.1, version/error/deprecation policy | All | Pydantic plus independent jsonschema and byte-pinned official OpenAPI schema; actual example/component validation | Same three directories |
| NFR-09; Q06/Q12/Q13 | Minimal scoped dependencies; deterministic real CI check; source/frozen integrity and review | Maintainers | Pinned requirements/actions/runtime, guarded nonzero/no-skip entry point, actual local checks and scoped diff | .github/workflows/contract-checks.yml plus three scoped directories |

All wire fields, required/null meanings, enums, identifier patterns and relation
constraints are documented in [DATA-DICTIONARY.md](DATA-DICTIONARY.md) and
[SEMANTICS.md](SEMANTICS.md). Consumer expectations and review choices are in
[CONSUMERS.md](CONSUMERS.md). Actual acceptance and local/hosted distinctions are
in [F02-REPORT.md](F02-REPORT.md).
