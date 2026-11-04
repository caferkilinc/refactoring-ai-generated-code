# CIR 1.0.0 data dictionary

Generated from the authoritative Pydantic registry and shared field descriptions.
Every wire field is required in v1. A nullable field is supplied explicitly as null;
null does not mean zero, false, empty, unsupported or successful.
Identifiers below are logical schema IDs, not deployed download URLs.

Cross-record and state-dependent constraints are defined in [SEMANTICS.md](SEMANTICS.md).

## AdapterRequest

One explicitly routed, bounded operation; no parser-implies-test assumption.

`urn:genesis:cir:1.0.0#/$defs/AdapterRequest`

| Field | Type | Required | Values / constraints | Meaning |
|---|---|---|---|---|
| `schema_version` | string | yes | {"const": "1.0.0"} | Exact supported schema version; v1 readers reject unknown versions and fields. |
| `scope` | Scope | yes | {} | Immutable project/version/analysis/run and baseline source binding. |
| `language` | string | yes | {"enum": ["JAVA", "PYTHON", "JAVASCRIPT", "TYPESCRIPT", "CSHARP", "GO", "CPP"]} | One of JAVA, PYTHON, JAVASCRIPT, TYPESCRIPT, CSHARP, GO or CPP; no silent language routing. |
| `component_id` | string | yes | {"pattern": "^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"} | component: boundary for per-language routing and capability evidence. |
| `adapter_capabilities_id` | string | yes | {"pattern": "^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"} | adaptercaps: reference to the language/component declaration used for routing. |
| `capability_id` | string | yes | {"pattern": "^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"} | capability: reference to the exact operation requested from the adapter. |
| `operation` | string | yes | {"enum": ["parse", "symbol", "quality", "dependency", "build", "test", "coverage", "safe_patch", "security"]} | Adapter capability being requested, or the changed-file operation ADD/MODIFY/DELETE. |
| `input_artifact_id` | string | yes | {"pattern": "^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"} | artifact: input reference for a routed adapter operation; authorize access before execution. |
| `timeout_seconds` | integer | yes | {"minimum": 1, "maximum": 3600} | Bounded operation timeout in seconds; future sandbox/tool execution must enforce it. |

## AdapterResult

Execution status remains distinct from behavioral, quality and security evidence.

`urn:genesis:cir:1.0.0#/$defs/AdapterResult`

| Field | Type | Required | Values / constraints | Meaning |
|---|---|---|---|---|
| `schema_version` | string | yes | {"const": "1.0.0"} | Exact supported schema version; v1 readers reject unknown versions and fields. |
| `operation` | string | yes | {"enum": ["parse", "symbol", "quality", "dependency", "build", "test", "coverage", "safe_patch", "security"]} | Adapter capability being requested, or the changed-file operation ADD/MODIFY/DELETE. |
| `execution_status` | string | yes | {"enum": ["COMPLETED", "FAILED", "NOT_RUN", "UNAVAILABLE", "INCOMPLETE"]} | COMPLETED, FAILED, NOT_RUN, UNAVAILABLE or INCOMPLETE; distinct from result dimensions. |
| `result` | ResultEnvelope or ErrorEnvelope | yes | {} | Versioned success or safe error envelope produced by a future adapter operation. |

## Artifact

Content-addressed opaque artifact reference; no local path or raw secret content.

`urn:genesis:cir:1.0.0#/$defs/Artifact`

| Field | Type | Required | Values / constraints | Meaning |
|---|---|---|---|---|
| `id` | string | yes | {"pattern": "^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"} | artifact: identifier resolved by the future authorized artifact service. |
| `sha256` | string | yes | {"pattern": "^[0-9a-f]{64}$"} | SHA-256 of actual artifact bytes, distinct from a Git object ID. |
| `media_type` | string | yes | {"minLength": 1, "maxLength": 2048} | Artifact MIME type. |
| `redaction` | string | yes | {"enum": ["MASKED", "NO_SENSITIVE_CONTENT", "UNREVIEWED", "FAILED"]} | Masking/review status; not a claim of scanner success. |

## Attempt

Failure-inclusive denominator ledger; not a worker implementation.

`urn:genesis:cir:1.0.0#/$defs/Attempt`

| Field | Type | Required | Values / constraints | Meaning |
|---|---|---|---|---|
| `id` | string | yes | {"pattern": "^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"} | attempt: identifier; never erased after failure. |
| `job_id` | string | yes | {"pattern": "^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"} | job: parent refactoring job. |
| `number` | integer | yes | {"minimum": 1, "maximum": 3} | One initial candidate plus at most two corrections. |
| `started` | boolean | yes | {} | Whether this planned attempt actually started. |
| `execution_status` | string | yes | {"enum": ["COMPLETED", "FAILED", "NOT_RUN", "UNAVAILABLE", "INCOMPLETE"]} | Execution outcome, independent of behavioral and quality results. |
| `reason` | string or null | yes | {} | Failure/unavailable/not-run explanation, or null after completion. |
| `failure_kind` | string or null | yes | {} | Explicit failure category, or null for completed/not-yet-failed work. |
| `evidence_ids` | array of string | yes | {} | evidence: references retaining the failure or actual attempt outcome. |
| `artifact_ids` | array of string | yes | {} | artifact: redacted failure/raw-rejection receipts; invalid proposals need not be admitted as valid PatchCandidates. |

## Capability

One language/component capability; parser support implies no other support.

`urn:genesis:cir:1.0.0#/$defs/Capability`

| Field | Type | Required | Values / constraints | Meaning |
|---|---|---|---|---|
| `schema_version` | string | yes | {"const": "1.0.0"} | Exact supported contract version. Unknown versions are rejected. |
| `id` | string | yes | {"pattern": "^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"} | Globally unique, type-prefixed immutable entity ID. |
| `scope` | Scope | yes | {} | Source/project/version/analysis/run binding. |
| `subject_sha256` | string | yes | {"pattern": "^[0-9a-f]{64}$"} | Actual observed source-manifest snapshot; baseline and candidate evidence must not be interchanged. |
| `recorded_at` | string | yes | {"pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(?:\\.\\d{1,6})?Z$"} | Actual UTC record timestamp; fixtures use an explicitly synthetic fixed timestamp. |
| `kind` | string | yes | {"const": "Capability"} | Discriminator naming the exact CIR entity schema; no implicit fallback to another entity. |
| `language` | string | yes | {"enum": ["JAVA", "PYTHON", "JAVASCRIPT", "TYPESCRIPT", "CSHARP", "GO", "CPP"]} | One of JAVA, PYTHON, JAVASCRIPT, TYPESCRIPT, CSHARP, GO or CPP; no silent language routing. |
| `component_id` | string | yes | {"pattern": "^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"} | component: boundary for per-language routing and capability evidence. |
| `capability` | string | yes | {"enum": ["parse", "symbol", "quality", "dependency", "build", "test", "coverage", "safe_patch", "security"]} | One independently declared operation; support for another operation does not imply support for this one. |
| `status` | string | yes | {"enum": ["SUPPORTED", "UNSUPPORTED", "UNAVAILABLE", "UNRESOLVED", "NOT_IMPLEMENTED"]} | Context-specific exact state enum; never collapse execution, behavior, quality, security and evidence states. |
| `confidence` | Confidence | yes | {} | Producer-reported score in [0,1] or explicit unknown reason; not an automatically calibrated probability. |
| `tool` | ToolProvenance or null | yes | {} | Observed tool identity/version/config provenance, or null for an unavailable capability. |
| `toolchain` | array of ToolchainRequirement | yes | {} | Required tools with observed availability/version; missing tools cannot imply support. |
| `evidence_ids` | array of string | yes | {} | evidence: provenance links; verification gates require independent VERIFIED evidence for the same snapshot. |
| `limitations` | array of string | yes | {} | Explicit capability restrictions and unmeasured assumptions. |
| `reason` | string or null | yes | {} | Explicit explanation for an unknown, unresolved, unavailable, incomplete or failed state; null when inapplicable. |

## ChangedFile

One portable source file operation with explicit before/after integrity metadata.

`urn:genesis:cir:1.0.0#/$defs/ChangedFile`

| Field | Type | Required | Values / constraints | Meaning |
|---|---|---|---|---|
| `file_id` | string | yes | {"pattern": "^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"} | file: identity in the appropriate source-snapshot manifest. |
| `path` | string | yes | {"minLength": 1, "maxLength": 2048} | Canonical NFC repository-relative source path; absolute, traversal, encoded separators and reserved filenames are rejected. |
| `operation` | string | yes | {"enum": ["ADD", "MODIFY", "DELETE"]} | Adapter capability being requested, or the changed-file operation ADD/MODIFY/DELETE. |
| `before_sha256` | string or null | yes | {} | Original file-byte SHA-256; null only when adding a new file. |
| `after_sha256` | string or null | yes | {} | Resulting file-byte SHA-256; null only for deletion. |

## ComparisonContext

Explicit reproducibility inputs behind a metric comparison fingerprint.

`urn:genesis:cir:1.0.0#/$defs/ComparisonContext`

| Field | Type | Required | Values / constraints | Meaning |
|---|---|---|---|---|
| `tool` | ToolProvenance | yes | {} | Observed tool identity/version/config provenance, or null for an unavailable capability. |
| `rule_set_version` | string or null | yes | {} | Observed ruleset/metric definition version; null if unknown. |
| `rule_set_reason` | string or null | yes | {} | Why the ruleset version is unknown; otherwise null. |
| `measurement_scope_sha256` | string | yes | {"pattern": "^[0-9a-f]{64}$"} | Fingerprint of the same target files/symbols/measurement definition, not their changing contents. |
| `environment_sha256` | string or null | yes | {} | Observed execution environment fingerprint, or null. |
| `environment_reason` | string or null | yes | {} | Why the environment fingerprint is unknown; otherwise null. |
| `test_suite_sha256` | string or null | yes | {} | Frozen suite fingerprint for test/coverage comparisons; null when not applicable or unknown. |
| `test_suite_state` | string | yes | {"enum": ["KNOWN", "NOT_APPLICABLE", "UNKNOWN"]} | Distinguishes an inapplicable suite from missing comparison context. |

## Confidence

Producer-reported confidence, not an automatically calibrated probability.

`urn:genesis:cir:1.0.0#/$defs/Confidence`

| Field | Type | Required | Values / constraints | Meaning |
|---|---|---|---|---|
| `value` | number or null | yes | {} | Normalized confidence or explicit null. |
| `reason` | string or null | yes | {} | Required when confidence is unknown; otherwise null. |

## ContextBudget

Request-specific token bound and honest measured/unknown token usage.

`urn:genesis:cir:1.0.0#/$defs/ContextBudget`

| Field | Type | Required | Values / constraints | Meaning |
|---|---|---|---|---|
| `max_tokens` | integer | yes | {"minimum": 1} | Positive context budget supplied for this request; never silently expanded. |
| `used_tokens` | integer or null | yes | {} | Observed token usage, or explicit null; never fabricate missing usage as zero. |
| `measurement` | string | yes | {"enum": ["MEASURED", "UNKNOWN"]} | Whether a value was actually MEASURED or remains explicitly UNKNOWN/UNAVAILABLE/NOT_APPLICABLE. |
| `reason` | string or null | yes | {} | Explicit explanation for an unknown, unresolved, unavailable, incomplete or failed state; null when inapplicable. |

## ContextExclusion

A deliberately excluded context reference and its reason.

`urn:genesis:cir:1.0.0#/$defs/ContextExclusion`

| Field | Type | Required | Values / constraints | Meaning |
|---|---|---|---|---|
| `reference_id` | string | yes | {"pattern": "^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"} | Opaque context reference recorded as excluded with an explicit reason. |
| `reason` | string | yes | {"minLength": 1, "maxLength": 2048} | Explicit explanation for an unknown, unresolved, unavailable, incomplete or failed state; null when inapplicable. |

## ContextPackage

Bounded reference-only context; sensitive raw source is not a contract field.

`urn:genesis:cir:1.0.0#/$defs/ContextPackage`

| Field | Type | Required | Values / constraints | Meaning |
|---|---|---|---|---|
| `schema_version` | string | yes | {"const": "1.0.0"} | Exact supported contract version. Unknown versions are rejected. |
| `id` | string | yes | {"pattern": "^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"} | Globally unique, type-prefixed immutable entity ID. |
| `scope` | Scope | yes | {} | Source/project/version/analysis/run binding. |
| `subject_sha256` | string | yes | {"pattern": "^[0-9a-f]{64}$"} | Actual observed source-manifest snapshot; baseline and candidate evidence must not be interchanged. |
| `recorded_at` | string | yes | {"pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(?:\\.\\d{1,6})?Z$"} | Actual UTC record timestamp; fixtures use an explicitly synthetic fixed timestamp. |
| `kind` | string | yes | {"const": "ContextPackage"} | Discriminator naming the exact CIR entity schema; no implicit fallback to another entity. |
| `selection_id` | string | yes | {"pattern": "^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"} | selection: reference to the immutable Gate 1 selection snapshot. |
| `target_finding_id` | string | yes | {"pattern": "^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"} | finding: one target present in the approved source-bound selection. |
| `target_symbol_id` | string or null | yes | {} | symbol: source-aligned target, or null for explicitly incomplete context. |
| `source_location_ids` | array of string | yes | {} | location: ranges supplied as bounded source context. |
| `caller_symbol_ids` | array of string | yes | {} | symbol: callers of the target, supported by corresponding CALL edges in complete context. |
| `callee_symbol_ids` | array of string | yes | {} | symbol: callees of the target, supported by corresponding CALL edges in complete context. |
| `dependency_ids` | array of string | yes | {} | dependency: relationships included in context; unresolved relationships prevent COMPLETE. |
| `test_result_ids` | array of string | yes | {} | test: actual executions on the validated source snapshot, not merely passing baseline tests. |
| `public_api_symbol_ids` | array of string | yes | {} | symbol: references whose public_api value is explicitly true in complete context. |
| `known_side_effects` | array of string | yes | {} | Observed side-effect descriptions; empty means known none only when side_effect_status is KNOWN. |
| `side_effect_status` | string | yes | {"enum": ["KNOWN", "UNKNOWN"]} | KNOWN or UNKNOWN; unknown effects prevent COMPLETE context. |
| `budget` | ContextBudget | yes | {} | Explicit context token limit and observed usage or unknown-usage reason. |
| `included_ids` | array of string | yes | {} | Closed set of included context references; must contain every declared critical reference when COMPLETE. |
| `excluded` | array of ContextExclusion | yes | {} | Explicitly excluded context references with reasons; never also listed as included. |
| `missing_critical_ids` | array of string | yes | {} | Critical context references that could not be supplied; nonempty forbids COMPLETE. |
| `unresolved_dependency_ids` | array of string | yes | {} | Explicit unresolved relationships; nonempty forbids COMPLETE context. |
| `artifact_ids` | array of string | yes | {} | artifact: references included in bounded context; complete context requires reviewed redaction states. |
| `redaction` | string | yes | {"enum": ["MASKED", "NO_SENSITIVE_CONTENT", "UNREVIEWED", "FAILED"]} | MASKED, NO_SENSITIVE_CONTENT, UNREVIEWED or FAILED; a declaration does not implement a redactor. |
| `evidence_ids` | array of string | yes | {} | evidence: provenance links; verification gates require independent VERIFIED evidence for the same snapshot. |
| `completeness` | string | yes | {"enum": ["COMPLETE", "INCOMPLETE"]} | COMPLETE only when critical references, side effects, redaction and budget are known; otherwise INCOMPLETE. |
| `reasons` | array of string | yes | {} | Human-readable rejection/incompleteness explanations; empty only when the relevant gate is satisfied. |

## ContractBundle

Closed reference graph for validation gates; standalone records validate only their shape.

`urn:genesis:cir:1.0.0#/$defs/ContractBundle`

| Field | Type | Required | Values / constraints | Meaning |
|---|---|---|---|---|
| `schema_version` | string | yes | {"const": "1.0.0"} | Exact supported schema version; v1 readers reject unknown versions and fields. |
| `mode` | string | yes | {"enum": ["FIXTURE", "INTERCHANGE"]} | FIXTURE examples do not claim real tool/model execution. |
| `scope` | Scope | yes | {} | Immutable project/version/analysis/run and baseline source binding. |
| `files` | array of FileIdentity | yes | {} | Source file inventory by snapshot/path, including symlink, frozen and protected-test flags. |
| `artifacts` | array of Artifact | yes | {} | Opaque artifact inventory with actual content hashes and redaction metadata. |
| `test_suites` | array of TestSuite | yes | {} | Frozen suite inventory; does not claim the suite has been executed. |
| `attempts` | array of Attempt | yes | {} | Failure-inclusive attempt ledger; started and planned populations remain distinct. |
| `records` | array of one of SourceLocation, Symbol, DependencyEdge, Evidence, Finding, Metric, TestResult, Capability, LanguageAdapterCapabilities, IssueSelection, ContextPackage, PatchCandidate, ValidationResult | yes | {"minItems": 1} | Typed CIR records in a closed graph; duplicate or wrong-kind identifiers are rejected. |

## DependencyEdge

Observed or unresolved symbol relationship; unknown edges remain visible.

`urn:genesis:cir:1.0.0#/$defs/DependencyEdge`

| Field | Type | Required | Values / constraints | Meaning |
|---|---|---|---|---|
| `schema_version` | string | yes | {"const": "1.0.0"} | Exact supported contract version. Unknown versions are rejected. |
| `id` | string | yes | {"pattern": "^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"} | Globally unique, type-prefixed immutable entity ID. |
| `scope` | Scope | yes | {} | Source/project/version/analysis/run binding. |
| `subject_sha256` | string | yes | {"pattern": "^[0-9a-f]{64}$"} | Actual observed source-manifest snapshot; baseline and candidate evidence must not be interchanged. |
| `recorded_at` | string | yes | {"pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(?:\\.\\d{1,6})?Z$"} | Actual UTC record timestamp; fixtures use an explicitly synthetic fixed timestamp. |
| `kind` | string | yes | {"const": "DependencyEdge"} | Discriminator naming the exact CIR entity schema; no implicit fallback to another entity. |
| `from_symbol_id` | string | yes | {"pattern": "^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"} | symbol: source of the observed dependency relationship. |
| `to_symbol_id` | string or null | yes | {} | symbol: dependency target, or null with an unresolved reason. |
| `relationship` | string | yes | {"enum": ["CALL", "READ", "WRITE", "IMPORT", "INHERIT", "UNKNOWN"]} | CALL, READ, WRITE, IMPORT, INHERIT or UNKNOWN; uncertain targets remain unresolved. |
| `resolution` | string | yes | {"enum": ["RESOLVED", "UNRESOLVED"]} | RESOLVED versus UNRESOLVED; coordinates or dependency targets cannot be fabricated to appear resolved. |
| `reason` | string or null | yes | {} | Explicit explanation for an unknown, unresolved, unavailable, incomplete or failed state; null when inapplicable. |
| `evidence_ids` | array of string | yes | {} | evidence: provenance links; verification gates require independent VERIFIED evidence for the same snapshot. |

## ErrorDetail

Safe structured failure metadata without reflecting raw inputs.

`urn:genesis:cir:1.0.0#/$defs/ErrorDetail`

| Field | Type | Required | Values / constraints | Meaning |
|---|---|---|---|---|
| `entity_id` | string or null | yes | {} | Optional type-prefixed entity reference; safe generated errors use null rather than reflecting untrusted input. |
| `field` | string or null | yes | {} | Safe field name identifying the contract failure without raw source content. |

## ErrorEnvelope

Safe API error without raw source, stack trace, credentials or host filesystem paths.

`urn:genesis:cir:1.0.0#/$defs/ErrorEnvelope`

| Field | Type | Required | Values / constraints | Meaning |
|---|---|---|---|---|
| `schema_version` | string | yes | {"const": "1.0.0"} | Exact supported schema version; v1 readers reject unknown versions and fields. |
| `request_id` | string | yes | {"pattern": "^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"} | request: identifier for correlating a safe API result/error with its request. |
| `status` | string | yes | {"const": "ERROR"} | Context-specific exact state enum; never collapse execution, behavior, quality, security and evidence states. |
| `code` | string | yes | {"enum": ["INVALID_CONTRACT", "BROKEN_REFERENCE", "SCOPE_MISMATCH", "STALE_SELECTION", "FORBIDDEN_SCOPE", "UNAVAILABLE_CAPABILITY", "INCOMPLETE_CONTEXT", "VALIDATION_FAILED", "INTERNAL_ERROR"]} | Stable machine-readable error code; clients must branch on this value rather than message text. |
| `component` | string | yes | {"enum": ["API", "CONTRACT", "ADAPTER", "CONTEXT", "VALIDATION"]} | Originating subsystem for an API error. |
| `message` | string | yes | {"minLength": 1, "maxLength": 2048} | Static safe user message; never reflect raw validation input. |
| `retryable` | boolean | yes | {} | Whether retry after resolving the reported condition may succeed; not permission for unbounded retries. |
| `details` | array of ErrorDetail | yes | {} | Safe structured entity/field error metadata; no raw input, stack trace, host path or credential. |

## Evidence

Attributable evidence; an LLM claim is never independent verified evidence.

`urn:genesis:cir:1.0.0#/$defs/Evidence`

| Field | Type | Required | Values / constraints | Meaning |
|---|---|---|---|---|
| `schema_version` | string | yes | {"const": "1.0.0"} | Exact supported contract version. Unknown versions are rejected. |
| `id` | string | yes | {"pattern": "^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"} | Globally unique, type-prefixed immutable entity ID. |
| `scope` | Scope | yes | {} | Source/project/version/analysis/run binding. |
| `subject_sha256` | string | yes | {"pattern": "^[0-9a-f]{64}$"} | Actual observed source-manifest snapshot; baseline and candidate evidence must not be interchanged. |
| `recorded_at` | string | yes | {"pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(?:\\.\\d{1,6})?Z$"} | Actual UTC record timestamp; fixtures use an explicitly synthetic fixed timestamp. |
| `kind` | string | yes | {"const": "Evidence"} | Discriminator naming the exact CIR entity schema; no implicit fallback to another entity. |
| `producer_kind` | string | yes | {"enum": ["DETERMINISTIC_TOOL", "HUMAN", "LLM"]} | DETERMINISTIC_TOOL, HUMAN or LLM; an LLM claim cannot independently be VERIFIED. |
| `actor_id` | string or null | yes | {} | actor: authenticated human reviewer identity for HUMAN evidence; otherwise null. |
| `tool` | ToolProvenance | yes | {} | Observed tool identity/version/config provenance, or null for an unavailable capability. |
| `rule_id` | string or null | yes | {} | Stable originating rule identity, or null where a producer has no applicable rule. |
| `model` | ModelProvenance or null | yes | {} | Provider/model/revision/settings provenance, with explicit reasons for unknown values. |
| `artifact_id` | string | yes | {"pattern": "^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"} | artifact: opaque reference to the attributed evidence artifact, never a local absolute path. |
| `location_ids` | array of string | yes | {} | location: source references; duplication findings require both source locations. |
| `symbol_ids` | array of string | yes | {} | symbol: references supporting the attributed evidence. |
| `verification` | string | yes | {"enum": ["VERIFIED", "UNCONFIRMED", "REJECTED", "UNAVAILABLE"]} | VERIFIED, UNCONFIRMED, REJECTED or UNAVAILABLE evidence state. |
| `confidence` | Confidence | yes | {} | Producer-reported score in [0,1] or explicit unknown reason; not an automatically calibrated probability. |
| `redaction` | string | yes | {"enum": ["MASKED", "NO_SENSITIVE_CONTENT", "UNREVIEWED", "FAILED"]} | MASKED, NO_SENSITIVE_CONTENT, UNREVIEWED or FAILED; a declaration does not implement a redactor. |

## FileIdentity

Trusted input manifest entry; candidate metadata cannot redefine this policy.

`urn:genesis:cir:1.0.0#/$defs/FileIdentity`

| Field | Type | Required | Values / constraints | Meaning |
|---|---|---|---|---|
| `id` | string | yes | {"pattern": "^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"} | file: identity of one source file in the snapshot. |
| `path` | string | yes | {"minLength": 1, "maxLength": 2048} | Canonical repository-relative path, with forward slashes. |
| `sha256` | string | yes | {"pattern": "^[0-9a-f]{64}$"} | SHA-256 of the original file bytes. |
| `subject_sha256` | string | yes | {"pattern": "^[0-9a-f]{64}$"} | Manifest snapshot that owns this file identity. |
| `is_symlink` | boolean | yes | {} | True for a linked entry; never eligible as a patch target. |
| `frozen` | boolean | yes | {} | Trusted immutable/frozen artifact flag. |
| `protected_test` | boolean | yes | {} | Trusted frozen or protected test flag. |

## Finding

Normalized quality/security/baseline observation with stable rule and evidence lineage.

`urn:genesis:cir:1.0.0#/$defs/Finding`

| Field | Type | Required | Values / constraints | Meaning |
|---|---|---|---|---|
| `schema_version` | string | yes | {"const": "1.0.0"} | Exact supported contract version. Unknown versions are rejected. |
| `id` | string | yes | {"pattern": "^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"} | Globally unique, type-prefixed immutable entity ID. |
| `scope` | Scope | yes | {} | Source/project/version/analysis/run binding. |
| `subject_sha256` | string | yes | {"pattern": "^[0-9a-f]{64}$"} | Actual observed source-manifest snapshot; baseline and candidate evidence must not be interchanged. |
| `recorded_at` | string | yes | {"pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(?:\\.\\d{1,6})?Z$"} | Actual UTC record timestamp; fixtures use an explicitly synthetic fixed timestamp. |
| `kind` | string | yes | {"const": "Finding"} | Discriminator naming the exact CIR entity schema; no implicit fallback to another entity. |
| `classification` | string | yes | {"enum": ["QUALITY_REFACTOR", "SECURITY_REVIEW", "BASELINE"]} | QUALITY_REFACTOR, SECURITY_REVIEW or BASELINE; only eligible quality findings may enter ordinary Gate 1. |
| `category` | string | yes | {"enum": ["QUALITY", "COMPLEXITY", "DUPLICATION", "SECURITY", "BASELINE"]} | UI/filter category; SECURITY and BASELINE must match the corresponding classification. |
| `rule_id` | string | yes | {"minLength": 1, "maxLength": 2048} | Stable originating rule identity, or null where a producer has no applicable rule. |
| `tool` | ToolProvenance | yes | {} | Observed tool identity/version/config provenance, or null for an unavailable capability. |
| `location_ids` | array of string | yes | {"minItems": 1} | location: source references; duplication findings require both source locations. |
| `evidence_ids` | array of string | yes | {"minItems": 1} | evidence: provenance links; verification gates require independent VERIFIED evidence for the same snapshot. |
| `confidence` | Confidence | yes | {} | Producer-reported score in [0,1] or explicit unknown reason; not an automatically calibrated probability. |
| `eligibility` | string | yes | {"enum": ["ELIGIBLE", "INELIGIBLE", "UNRESOLVED"]} | Finding/selection gate state; not equivalent to successful execution or product approval by itself. |
| `eligibility_reason` | string or null | yes | {} | Explicit explanation when a finding is ineligible or unresolved. |
| `status` | string | yes | {"enum": ["OPEN", "RESOLVED", "SUPPRESSED", "UNVERIFIED"]} | Context-specific exact state enum; never collapse execution, behavior, quality, security and evidence states. |

## FindingSnapshot

Immutable complete-Finding fingerprint recorded by Gate 1.

`urn:genesis:cir:1.0.0#/$defs/FindingSnapshot`

| Field | Type | Required | Values / constraints | Meaning |
|---|---|---|---|---|
| `finding_id` | string | yes | {"pattern": "^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"} | finding: reference bound by the adjacent immutable snapshot fingerprint. |
| `fingerprint` | string | yes | {"pattern": "^[0-9a-f]{64}$"} | SHA-256 of canonical JSON of the complete selected Finding record. |

## IssueSelection

Approval Gate 1: immutable, source-bound selection snapshot, not an approval service.

`urn:genesis:cir:1.0.0#/$defs/IssueSelection`

| Field | Type | Required | Values / constraints | Meaning |
|---|---|---|---|---|
| `schema_version` | string | yes | {"const": "1.0.0"} | Exact supported contract version. Unknown versions are rejected. |
| `id` | string | yes | {"pattern": "^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"} | Globally unique, type-prefixed immutable entity ID. |
| `scope` | Scope | yes | {} | Source/project/version/analysis/run binding. |
| `subject_sha256` | string | yes | {"pattern": "^[0-9a-f]{64}$"} | Actual observed source-manifest snapshot; baseline and candidate evidence must not be interchanged. |
| `recorded_at` | string | yes | {"pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(?:\\.\\d{1,6})?Z$"} | Actual UTC record timestamp; fixtures use an explicitly synthetic fixed timestamp. |
| `kind` | string | yes | {"const": "IssueSelection"} | Discriminator naming the exact CIR entity schema; no implicit fallback to another entity. |
| `selected_finding_ids` | array of string | yes | {"minItems": 1} | finding: Gate 1 choices; only current eligible QUALITY_REFACTOR findings can be approved. |
| `baseline_test_result_ids` | array of string | yes | {"minItems": 1} | test: baseline executions supporting Gate 1; eligible selections require nonempty passing baseline evidence. |
| `snapshots` | array of FindingSnapshot | yes | {"minItems": 1} | Selected finding IDs plus complete-record RFC 8785/SHA-256 fingerprints, sorted for the selection fingerprint. |
| `fingerprint` | string | yes | {"pattern": "^[0-9a-f]{64}$"} | Canonical scope+sorted snapshot fingerprint; excludes this field itself. |
| `actor_id` | string | yes | {"pattern": "^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"} | actor: identity of the human making the product selection; authenticate outside this data contract. |
| `created_at` | string | yes | {"pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(?:\\.\\d{1,6})?Z$"} | UTC timestamp of the immutable issue-selection decision, using a Z suffix. |
| `approval_ref` | string | yes | {"pattern": "^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"} | approval: audit reference for Gate 1; the string itself does not authenticate an approval. |
| `eligibility` | string | yes | {"enum": ["ELIGIBLE", "REJECTED", "UNRESOLVED"]} | Finding/selection gate state; not equivalent to successful execution or product approval by itself. |
| `reasons` | array of string | yes | {} | Human-readable rejection/incompleteness explanations; empty only when the relevant gate is satisfied. |

## LanguageAdapterCapabilities

Shared adapter declaration, independently covering all nine capability dimensions.

`urn:genesis:cir:1.0.0#/$defs/LanguageAdapterCapabilities`

| Field | Type | Required | Values / constraints | Meaning |
|---|---|---|---|---|
| `schema_version` | string | yes | {"const": "1.0.0"} | Exact supported contract version. Unknown versions are rejected. |
| `id` | string | yes | {"pattern": "^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"} | Globally unique, type-prefixed immutable entity ID. |
| `scope` | Scope | yes | {} | Source/project/version/analysis/run binding. |
| `subject_sha256` | string | yes | {"pattern": "^[0-9a-f]{64}$"} | Actual observed source-manifest snapshot; baseline and candidate evidence must not be interchanged. |
| `recorded_at` | string | yes | {"pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(?:\\.\\d{1,6})?Z$"} | Actual UTC record timestamp; fixtures use an explicitly synthetic fixed timestamp. |
| `kind` | string | yes | {"const": "LanguageAdapterCapabilities"} | Discriminator naming the exact CIR entity schema; no implicit fallback to another entity. |
| `adapter_id` | string | yes | {"pattern": "^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"} | adapter: stable implementation/interface identity; a declaration does not prove runtime availability. |
| `language` | string | yes | {"enum": ["JAVA", "PYTHON", "JAVASCRIPT", "TYPESCRIPT", "CSHARP", "GO", "CPP"]} | One of JAVA, PYTHON, JAVASCRIPT, TYPESCRIPT, CSHARP, GO or CPP; no silent language routing. |
| `component_id` | string | yes | {"pattern": "^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"} | component: boundary for per-language routing and capability evidence. |
| `implementation_state` | string | yes | {"enum": ["CONTRACT_DEFINED", "RUNTIME_IMPLEMENTED"]} | CONTRACT_DEFINED versus RUNTIME_IMPLEMENTED; the latter needs at least one genuinely supported capability. |
| `capability_ids` | array of string | yes | {"minItems": 9, "maxItems": 9} | Exactly one reference for each of parse, symbol, quality, dependency, build, test, coverage, safe_patch and security. |

## Metric

Measured quantity with comparison fingerprint and failure-inclusive population.

`urn:genesis:cir:1.0.0#/$defs/Metric`

| Field | Type | Required | Values / constraints | Meaning |
|---|---|---|---|---|
| `schema_version` | string | yes | {"const": "1.0.0"} | Exact supported contract version. Unknown versions are rejected. |
| `id` | string | yes | {"pattern": "^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"} | Globally unique, type-prefixed immutable entity ID. |
| `scope` | Scope | yes | {} | Source/project/version/analysis/run binding. |
| `subject_sha256` | string | yes | {"pattern": "^[0-9a-f]{64}$"} | Actual observed source-manifest snapshot; baseline and candidate evidence must not be interchanged. |
| `recorded_at` | string | yes | {"pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(?:\\.\\d{1,6})?Z$"} | Actual UTC record timestamp; fixtures use an explicitly synthetic fixed timestamp. |
| `kind` | string | yes | {"const": "Metric"} | Discriminator naming the exact CIR entity schema; no implicit fallback to another entity. |
| `name` | string | yes | {"minLength": 1, "maxLength": 2048} | Observed human-readable identity or metric name; not a substitute for stable typed IDs. |
| `unit` | string | yes | {"enum": ["COUNT", "PERCENT", "MILLISECONDS", "TOKENS", "CURRENCY"]} | Explicit COUNT, PERCENT, MILLISECONDS, TOKENS or CURRENCY unit; consumers must not mix denominators. |
| `currency_code` | string or null | yes | {} | Explicit ISO-style three-letter currency code for CURRENCY, otherwise null; never inferred from a provider name. |
| `phase` | string | yes | {"enum": ["BASELINE", "CANDIDATE"]} | Whether the metric measures BASELINE or CANDIDATE bytes. |
| `value` | number or null | yes | {} | Observed value or explicit null; confidence and metric domains define their own constraints. |
| `measurement` | string | yes | {"enum": ["MEASURED", "UNKNOWN", "UNAVAILABLE", "NOT_APPLICABLE"]} | Whether a value was actually MEASURED or remains explicitly UNKNOWN/UNAVAILABLE/NOT_APPLICABLE. |
| `reason` | string or null | yes | {} | Explicit explanation for an unknown, unresolved, unavailable, incomplete or failed state; null when inapplicable. |
| `comparison_key` | string | yes | {"pattern": "^[0-9a-f]{64}$"} | Fingerprint of tool/rules/config/measurement scope; excludes measured value. |
| `comparison` | ComparisonContext | yes | {} | Actual comparable inputs; comparison_key is checked against these fields, not trusted as an opaque claim. |
| `direction` | string | yes | {"enum": ["LOWER_IS_BETTER", "HIGHER_IS_BETTER", "CONTEXTUAL"]} | How a comparable measurement changes quality: lower, higher, or contextual with no automatic ranking. |
| `population` | string | yes | {"enum": ["NONE", "STARTED_ATTEMPTS", "PLANNED_ATTEMPTS"]} | NONE, STARTED_ATTEMPTS or PLANNED_ATTEMPTS; determines the required failure-inclusive denominator. |
| `denominator` | integer or null | yes | {} | Actual size of the declared attempt population; zero yields N/A rather than a fabricated zero ratio. |
| `attempt_ids` | array of string | yes | {} | Exactly the attempt population used by this measurement, retaining failed attempts. |
| `evidence_ids` | array of string | yes | {} | evidence: provenance links; verification gates require independent VERIFIED evidence for the same snapshot. |

## ModelProvenance

Provider/model attribution without guessing deployment or generation settings.

`urn:genesis:cir:1.0.0#/$defs/ModelProvenance`

| Field | Type | Required | Values / constraints | Meaning |
|---|---|---|---|---|
| `provider` | string | yes | {"minLength": 1, "maxLength": 2048} | Provider identity; local providers are allowed. |
| `model` | string | yes | {"minLength": 1, "maxLength": 2048} | Reported model name; not proof that an integration exists. |
| `revision` | string or null | yes | {} | Exact observed model revision, or null. |
| `revision_reason` | string or null | yes | {} | Why the exact revision is unknown, or null. |
| `settings` | object or null | yes | {} | Observed non-secret generation settings, or null. |
| `settings_reason` | string or null | yes | {} | Why settings are unknown, or null when known. |

## PatchCandidate

Proposed derivative patch metadata; never applies a patch or changes V0.

`urn:genesis:cir:1.0.0#/$defs/PatchCandidate`

| Field | Type | Required | Values / constraints | Meaning |
|---|---|---|---|---|
| `schema_version` | string | yes | {"const": "1.0.0"} | Exact supported contract version. Unknown versions are rejected. |
| `id` | string | yes | {"pattern": "^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"} | Globally unique, type-prefixed immutable entity ID. |
| `scope` | Scope | yes | {} | Source/project/version/analysis/run binding. |
| `subject_sha256` | string | yes | {"pattern": "^[0-9a-f]{64}$"} | Actual observed source-manifest snapshot; baseline and candidate evidence must not be interchanged. |
| `recorded_at` | string | yes | {"pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(?:\\.\\d{1,6})?Z$"} | Actual UTC record timestamp; fixtures use an explicitly synthetic fixed timestamp. |
| `kind` | string | yes | {"const": "PatchCandidate"} | Discriminator naming the exact CIR entity schema; no implicit fallback to another entity. |
| `job_id` | string | yes | {"pattern": "^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"} | job: parent refactoring job identity; separate from attempts and provider transport retries. |
| `attempt_id` | string | yes | {"pattern": "^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"} | attempt: reference to a started attempt belonging to the same job. |
| `selection_id` | string | yes | {"pattern": "^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"} | selection: reference to the immutable Gate 1 selection snapshot. |
| `target_finding_id` | string | yes | {"pattern": "^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"} | finding: one target present in the approved source-bound selection. |
| `technique` | string | yes | {"minLength": 1, "maxLength": 2048} | Named proposed refactoring technique; not proof of quality improvement. |
| `diff_artifact_id` | string | yes | {"pattern": "^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"} | artifact: opaque reference to proposed unified-diff bytes; metadata validation never applies the diff. |
| `diff_sha256` | string | yes | {"pattern": "^[0-9a-f]{64}$"} | SHA-256 of the diff artifact bytes, matched to the artifact inventory. |
| `output_snapshot_sha256` | string or null | yes | {} | Observed candidate source-manifest hash; null before materialization. |
| `output_manifest_artifact_id` | string or null | yes | {} | artifact: reference to the materialized candidate source manifest; null before it exists. |
| `output_snapshot_reason` | string or null | yes | {} | Why the candidate source snapshot is unknown; null when its hash and artifact are known. |
| `allowed_paths` | array of string | yes | {"minItems": 1} | Candidate-declared exact paths or directory prefixes ending in slash; intersect with independent PatchPolicy. |
| `changed_files` | array of ChangedFile | yes | {"minItems": 1} | Explicit file/operation/before/after manifest checked against independently trusted source metadata. |
| `model` | ModelProvenance | yes | {} | Provider/model/revision/settings provenance, with explicit reasons for unknown values. |
| `validation_ids` | array of string | yes | {} | validation: reciprocal references to actual assessments of this candidate. |
| `security_finding_ids` | array of string | yes | {} | finding: references restricted to SECURITY_REVIEW findings. |
| `security_status` | string | yes | {"enum": ["CLEAN", "FINDINGS", "NOT_RUN", "UNAVAILABLE", "INCOMPLETE"]} | CLEAN or FINDINGS only after a completed evidenced scan; absence is explicit. |
| `behavior_status` | string | yes | {"enum": ["PASSED", "FAILED", "UNVERIFIED"]} | PASSED, FAILED or UNVERIFIED, based on actual snapshot-matched test evidence. |
| `quality_outcome` | string | yes | {"enum": ["IMPROVED", "UNCHANGED", "WORSE", "NOT_COMPARABLE"]} | IMPROVED, UNCHANGED, WORSE or NOT_COMPARABLE, independently from behavior_status. |
| `applicability` | string | yes | {"enum": ["APPLICABLE", "REJECTED", "UNVERIFIED"]} | Patch metadata applicability, independent of approval, behavioral safety and quality improvement. |
| `rejection_reasons` | array of string | yes | {} | Reasons why a proposed patch is rejected or remains unverified. |
| `confidence` | Confidence | yes | {} | Producer-reported score in [0,1] or explicit unknown reason; not an automatically calibrated probability. |

## ResultEnvelope

Versioned successful API result; references are validated as a closed graph.

`urn:genesis:cir:1.0.0#/$defs/ResultEnvelope`

| Field | Type | Required | Values / constraints | Meaning |
|---|---|---|---|---|
| `schema_version` | string | yes | {"const": "1.0.0"} | Exact supported schema version; v1 readers reject unknown versions and fields. |
| `request_id` | string | yes | {"pattern": "^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"} | request: identifier for correlating a safe API result/error with its request. |
| `status` | string | yes | {"const": "OK"} | Context-specific exact state enum; never collapse execution, behavior, quality, security and evidence states. |
| `data` | ContractBundle | yes | {} | Versioned result bundle; gates additionally require cross-record validation with trusted policy inputs. |
| `next_cursor` | string or null | yes | {} | Opaque cursor; null means no additional page. |

## Scope

Identity of one immutable source snapshot and repeat analysis/run.

`urn:genesis:cir:1.0.0#/$defs/Scope`

| Field | Type | Required | Values / constraints | Meaning |
|---|---|---|---|---|
| `project_id` | string | yes | {"pattern": "^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"} | Project registry ID; project: prefix. |
| `version_id` | string | yes | {"pattern": "^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"} | Immutable project version ID; version: prefix. |
| `analysis_id` | string | yes | {"pattern": "^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"} | Analysis ID; analysis: prefix; fresh for a repeat analysis. |
| `run_id` | string | yes | {"pattern": "^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"} | Execution run ID; run: prefix; never reused for a retry. |
| `source_revision` | string | yes | {"pattern": "^[0-9a-f]{40}$"} | Git object SHA-1 of the source, not a file SHA-256. |
| `baseline_sha256` | string | yes | {"pattern": "^[0-9a-f]{64}$"} | SHA-256 of the immutable source manifest bytes. |

## SourceLocation

1-based lines and Unicode-scalar columns; range end is exclusive.

`urn:genesis:cir:1.0.0#/$defs/SourceLocation`

| Field | Type | Required | Values / constraints | Meaning |
|---|---|---|---|---|
| `schema_version` | string | yes | {"const": "1.0.0"} | Exact supported contract version. Unknown versions are rejected. |
| `id` | string | yes | {"pattern": "^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"} | Globally unique, type-prefixed immutable entity ID. |
| `scope` | Scope | yes | {} | Source/project/version/analysis/run binding. |
| `subject_sha256` | string | yes | {"pattern": "^[0-9a-f]{64}$"} | Actual observed source-manifest snapshot; baseline and candidate evidence must not be interchanged. |
| `recorded_at` | string | yes | {"pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(?:\\.\\d{1,6})?Z$"} | Actual UTC record timestamp; fixtures use an explicitly synthetic fixed timestamp. |
| `kind` | string | yes | {"const": "SourceLocation"} | Discriminator naming the exact CIR entity schema; no implicit fallback to another entity. |
| `path` | string or null | yes | {} | Portable source path; null only for an unresolved location. |
| `file_id` | string or null | yes | {} | file: reference, or null when unresolved. |
| `file_sha256` | string or null | yes | {} | Original source-file SHA-256, or null when unresolved. |
| `resolution` | string | yes | {"enum": ["RESOLVED", "UNRESOLVED"]} | RESOLVED versus UNRESOLVED; coordinates or dependency targets cannot be fabricated to appear resolved. |
| `reason` | string or null | yes | {} | Explicit unresolved reason, otherwise null. |
| `start_line` | integer or null | yes | {} | Inclusive 1-based line; LF and CRLF each separate one logical line. |
| `start_column` | integer or null | yes | {} | Inclusive 1-based Unicode-scalar column; a tab and an emoji each count as one scalar. |
| `end_line` | integer or null | yes | {} | 1-based end line; range end must lexicographically follow range start. |
| `end_column` | integer or null | yes | {} | Exclusive 1-based Unicode-scalar column; null only for unresolved coordinates. |
| `symbol_id` | string or null | yes | {} | Optional symbol: reference; null means no resolved symbol. |

## Symbol

Language-independent symbol identity with explicit resolution uncertainty.

`urn:genesis:cir:1.0.0#/$defs/Symbol`

| Field | Type | Required | Values / constraints | Meaning |
|---|---|---|---|---|
| `schema_version` | string | yes | {"const": "1.0.0"} | Exact supported contract version. Unknown versions are rejected. |
| `id` | string | yes | {"pattern": "^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"} | Globally unique, type-prefixed immutable entity ID. |
| `scope` | Scope | yes | {} | Source/project/version/analysis/run binding. |
| `subject_sha256` | string | yes | {"pattern": "^[0-9a-f]{64}$"} | Actual observed source-manifest snapshot; baseline and candidate evidence must not be interchanged. |
| `recorded_at` | string | yes | {"pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(?:\\.\\d{1,6})?Z$"} | Actual UTC record timestamp; fixtures use an explicitly synthetic fixed timestamp. |
| `kind` | string | yes | {"const": "Symbol"} | Discriminator naming the exact CIR entity schema; no implicit fallback to another entity. |
| `language` | string | yes | {"enum": ["JAVA", "PYTHON", "JAVASCRIPT", "TYPESCRIPT", "CSHARP", "GO", "CPP"]} | One of JAVA, PYTHON, JAVASCRIPT, TYPESCRIPT, CSHARP, GO or CPP; no silent language routing. |
| `name` | string | yes | {"minLength": 1, "maxLength": 2048} | Observed human-readable identity or metric name; not a substitute for stable typed IDs. |
| `signature` | string or null | yes | {} | Observed symbol signature; null when it cannot be established. |
| `location_id` | string | yes | {"pattern": "^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"} | location: source range associated with a symbol. |
| `resolution` | string | yes | {"enum": ["RESOLVED", "UNRESOLVED"]} | RESOLVED versus UNRESOLVED; coordinates or dependency targets cannot be fabricated to appear resolved. |
| `reason` | string or null | yes | {} | Explicit explanation for an unknown, unresolved, unavailable, incomplete or failed state; null when inapplicable. |
| `public_api` | boolean or null | yes | {} | Null means visibility is unknown; it is not equivalent to private. |
| `evidence_ids` | array of string | yes | {} | evidence: provenance links; verification gates require independent VERIFIED evidence for the same snapshot. |

## TestResult

One actual frozen-suite execution; a build is not a test result.

`urn:genesis:cir:1.0.0#/$defs/TestResult`

| Field | Type | Required | Values / constraints | Meaning |
|---|---|---|---|---|
| `schema_version` | string | yes | {"const": "1.0.0"} | Exact supported contract version. Unknown versions are rejected. |
| `id` | string | yes | {"pattern": "^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"} | Globally unique, type-prefixed immutable entity ID. |
| `scope` | Scope | yes | {} | Source/project/version/analysis/run binding. |
| `subject_sha256` | string | yes | {"pattern": "^[0-9a-f]{64}$"} | Actual observed source-manifest snapshot; baseline and candidate evidence must not be interchanged. |
| `recorded_at` | string | yes | {"pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(?:\\.\\d{1,6})?Z$"} | Actual UTC record timestamp; fixtures use an explicitly synthetic fixed timestamp. |
| `kind` | string | yes | {"const": "TestResult"} | Discriminator naming the exact CIR entity schema; no implicit fallback to another entity. |
| `suite_id` | string | yes | {"pattern": "^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"} | suite: immutable frozen baseline test-suite identity. |
| `suite_sha256` | string | yes | {"pattern": "^[0-9a-f]{64}$"} | SHA-256 of frozen test-suite manifest bytes, matched to the suite inventory. |
| `tool` | ToolProvenance | yes | {} | Observed tool identity/version/config provenance, or null for an unavailable capability. |
| `environment_sha256` | string or null | yes | {} | Observed test environment fingerprint, or null when execution cannot establish it. |
| `execution_status` | string | yes | {"enum": ["COMPLETED", "FAILED", "NOT_RUN", "UNAVAILABLE", "INCOMPLETE"]} | COMPLETED, FAILED, NOT_RUN, UNAVAILABLE or INCOMPLETE; distinct from result dimensions. |
| `outcome` | string | yes | {"enum": ["PASSED", "FAILED", "UNVERIFIED"]} | Observed test-suite result; a nonempty completed suite is required for PASSED. |
| `total` | integer or null | yes | {} | Observed total test cases; must equal passed+failed+skipped and the frozen suite case inventory. |
| `passed` | integer or null | yes | {} | Observed passing test count, or null when unknown. |
| `failed` | integer or null | yes | {} | Observed failing test count, or null when unknown; execution failure alone is not a failing test case. |
| `skipped` | integer or null | yes | {} | Observed skipped-test count; skipped cases do not establish full behavioral PASS. |
| `reason` | string or null | yes | {} | Explicit explanation for an unknown, unresolved, unavailable, incomplete or failed state; null when inapplicable. |
| `evidence_ids` | array of string | yes | {} | evidence: provenance links; verification gates require independent VERIFIED evidence for the same snapshot. |

## TestSuite

Frozen test identity, separate from a particular test execution.

`urn:genesis:cir:1.0.0#/$defs/TestSuite`

| Field | Type | Required | Values / constraints | Meaning |
|---|---|---|---|---|
| `id` | string | yes | {"pattern": "^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"} | suite: immutable baseline test-suite identifier. |
| `sha256` | string | yes | {"pattern": "^[0-9a-f]{64}$"} | SHA-256 of the frozen test-suite manifest bytes. |
| `case_ids` | array of string | yes | {} | Stable case: identifiers, including failed cases. |

## ToolProvenance

Actual tool/version/config lineage; unavailable values stay unknown.

`urn:genesis:cir:1.0.0#/$defs/ToolProvenance`

| Field | Type | Required | Values / constraints | Meaning |
|---|---|---|---|---|
| `tool_id` | string | yes | {"minLength": 1, "maxLength": 2048} | Tool product or adapter identity. |
| `version` | string or null | yes | {} | Observed tool version; null if unknown. |
| `version_reason` | string or null | yes | {} | Why the version is unknown, or null when known. |
| `config_sha256` | string or null | yes | {} | Actual configuration fingerprint, never an invented default. |
| `config_reason` | string or null | yes | {} | Why configuration is unavailable, or null when known. |

## ToolchainRequirement

Observed availability and version of a required toolchain component.

`urn:genesis:cir:1.0.0#/$defs/ToolchainRequirement`

| Field | Type | Required | Values / constraints | Meaning |
|---|---|---|---|---|
| `name` | string | yes | {"minLength": 1, "maxLength": 2048} | Observed human-readable identity or metric name; not a substitute for stable typed IDs. |
| `version` | string or null | yes | {} | Observed toolchain/tool version, with explicit unavailable/unknown semantics. |
| `status` | string | yes | {"enum": ["AVAILABLE", "UNAVAILABLE", "UNRESOLVED"]} | Context-specific exact state enum; never collapse execution, behavior, quality, security and evidence states. |
| `reason` | string or null | yes | {} | Explicit explanation for an unknown, unresolved, unavailable, incomplete or failed state; null when inapplicable. |

## ValidationResult

Evidence-backed independent behavior, quality, security and execution dimensions.

`urn:genesis:cir:1.0.0#/$defs/ValidationResult`

| Field | Type | Required | Values / constraints | Meaning |
|---|---|---|---|---|
| `schema_version` | string | yes | {"const": "1.0.0"} | Exact supported contract version. Unknown versions are rejected. |
| `id` | string | yes | {"pattern": "^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"} | Globally unique, type-prefixed immutable entity ID. |
| `scope` | Scope | yes | {} | Source/project/version/analysis/run binding. |
| `subject_sha256` | string | yes | {"pattern": "^[0-9a-f]{64}$"} | Actual observed source-manifest snapshot; baseline and candidate evidence must not be interchanged. |
| `recorded_at` | string | yes | {"pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(?:\\.\\d{1,6})?Z$"} | Actual UTC record timestamp; fixtures use an explicitly synthetic fixed timestamp. |
| `kind` | string | yes | {"const": "ValidationResult"} | Discriminator naming the exact CIR entity schema; no implicit fallback to another entity. |
| `candidate_ids` | array of string | yes | {"minItems": 1} | patch: candidates assessed by this result; individual validation requires exactly one. |
| `validation_scope` | string | yes | {"enum": ["CANDIDATE", "COMBINED"]} | CANDIDATE versus COMBINED; individual success does not establish combined success. |
| `workspace_kind` | string | yes | {"enum": ["CANDIDATE_DERIVATIVE", "FRESH_V0_COMBINATION"]} | CANDIDATE_DERIVATIVE versus FRESH_V0_COMBINATION; combined results require a fresh V0 workspace. |
| `workspace_manifest_artifact_id` | string | yes | {"pattern": "^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"} | artifact: validated workspace manifest, whose hash must match the result subject snapshot. |
| `execution_status` | string | yes | {"enum": ["COMPLETED", "FAILED", "NOT_RUN", "UNAVAILABLE", "INCOMPLETE"]} | COMPLETED, FAILED, NOT_RUN, UNAVAILABLE or INCOMPLETE; distinct from result dimensions. |
| `build_status` | string | yes | {"enum": ["PASSED", "FAILED", "UNVERIFIED"]} | Build outcome, kept separate from behavioral and quality outcomes. |
| `behavior_status` | string | yes | {"enum": ["PASSED", "FAILED", "UNVERIFIED"]} | PASSED, FAILED or UNVERIFIED, based on actual snapshot-matched test evidence. |
| `behavior_reason` | string or null | yes | {} | Explanation when behavior is UNVERIFIED; a build alone cannot establish preservation. |
| `quality_outcome` | string | yes | {"enum": ["IMPROVED", "UNCHANGED", "WORSE", "NOT_COMPARABLE"]} | IMPROVED, UNCHANGED, WORSE or NOT_COMPARABLE, independently from behavior_status. |
| `quality_reason` | string or null | yes | {} | Explanation when the measurements cannot support a comparison. |
| `security_status` | string | yes | {"enum": ["CLEAN", "FINDINGS", "NOT_RUN", "UNAVAILABLE", "INCOMPLETE"]} | CLEAN or FINDINGS only after a completed evidenced scan; absence is explicit. |
| `security_reason` | string or null | yes | {} | Explanation when scanning is unavailable, incomplete or not run. |
| `security_execution_status` | string | yes | {"enum": ["COMPLETED", "FAILED", "NOT_RUN", "UNAVAILABLE", "INCOMPLETE"]} | Whether the security scan actually completed, independent of overall execution. |
| `security_evidence_ids` | array of string | yes | {} | evidence: independent deterministic/human scan evidence for the exact validated snapshot. |
| `security_finding_ids` | array of string | yes | {} | finding: references restricted to SECURITY_REVIEW findings. |
| `test_result_ids` | array of string | yes | {} | test: actual executions on the validated source snapshot, not merely passing baseline tests. |
| `metric_ids` | array of string | yes | {} | metric: comparable before/after measurements supporting the quality outcome. |
| `evidence_ids` | array of string | yes | {} | evidence: provenance links; verification gates require independent VERIFIED evidence for the same snapshot. |
| `reason` | string or null | yes | {} | Explicit explanation for an unknown, unresolved, unavailable, incomplete or failed state; null when inapplicable. |
