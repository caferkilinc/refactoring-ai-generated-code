"""Strict wire models. Cross-record invariants live in validation.py.

All nullable fields are required unless a default is explicitly specified.
Missing information is represented by null plus a reason, never a guessed value.
"""
from __future__ import annotations

import re
import unicodedata
from datetime import datetime
from typing import Annotated, Literal, Union

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, model_validator

VERSION = '1.0.0'
SCHEMA_ID = 'urn:genesis:cir:1.0.0'
LANGUAGES = ('JAVA', 'PYTHON', 'JAVASCRIPT', 'TYPESCRIPT', 'CSHARP', 'GO', 'CPP')
CAPABILITIES = ('parse', 'symbol', 'quality', 'dependency', 'build', 'test', 'coverage',
                'safe_patch', 'security')


def unicode_scalars(value: str) -> str:
    try:
        value.encode('utf-8', errors='strict')
    except UnicodeEncodeError:
        raise ValueError('text must contain valid Unicode scalars') from None
    return value


Text = Annotated[str, Field(min_length=1, max_length=2048), AfterValidator(unicode_scalars)]
Identifier = Annotated[str, Field(pattern=r'^[a-z][a-z0-9_]*:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$')]
Sha256 = Annotated[str, Field(pattern=r'^[0-9a-f]{64}$')]
GitRevision = Annotated[str, Field(pattern=r'^[0-9a-f]{40}$')]
Language = Literal['JAVA', 'PYTHON', 'JAVASCRIPT', 'TYPESCRIPT', 'CSHARP', 'GO', 'CPP']
CapabilityName = Literal['parse', 'symbol', 'quality', 'dependency', 'build', 'test',
                         'coverage', 'safe_patch', 'security']
ExecutionStatus = Literal['COMPLETED', 'FAILED', 'NOT_RUN', 'UNAVAILABLE', 'INCOMPLETE']
BehaviorStatus = Literal['PASSED', 'FAILED', 'UNVERIFIED']
QualityOutcome = Literal['IMPROVED', 'UNCHANGED', 'WORSE', 'NOT_COMPARABLE']
SecurityStatus = Literal['CLEAN', 'FINDINGS', 'NOT_RUN', 'UNAVAILABLE', 'INCOMPLETE']
RedactionStatus = Literal['MASKED', 'NO_SENSITIVE_CONTENT', 'UNREVIEWED', 'FAILED']


def portable_path(value: str) -> str:
    """Canonical repository-relative NFC path; validation never rewrites input."""
    if value != unicodedata.normalize('NFC', value) or not value or value.startswith('/'):
        raise ValueError('path must be repository-relative and NFC normalized')
    if re.search(r'[\\:%\x00-\x1f\x7f]', value):
        raise ValueError('path contains a prohibited separator, encoding or control character')
    for part in value.split('/'):
        if part in ('', '.', '..') or part.casefold() == '.git' or part.endswith(('.', ' ')):
            raise ValueError('path contains an unsafe segment')
        if re.fullmatch(r'(?i)(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?', part):
            raise ValueError('path contains a reserved portable filename')
    return value


def scope_path(value: str) -> str:
    portable_path(value[:-1] if value.endswith('/') else value)
    return value


def utc_timestamp(value: str) -> str:
    if not value.endswith('Z'):
        raise ValueError('UTC timestamps must use a Z suffix')
    datetime.fromisoformat(value[:-1] + '+00:00')
    return value


PathValue = Annotated[Text, AfterValidator(portable_path)]
ScopePath = Annotated[Text, AfterValidator(scope_path)]
UtcTimestamp = Annotated[str, Field(pattern=r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z$'),
                         AfterValidator(utc_timestamp)]


def unknown(value, reason, field: str):
    if (value is None) != (reason is not None):
        raise ValueError(f'{field}: null requires a reason; a known value requires a null reason')


class ContractModel(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True, allow_inf_nan=False)


class Scope(ContractModel):
    """Identity of one immutable source snapshot and repeat analysis/run."""
    project_id: Identifier = Field(description='Project registry ID; project: prefix.')
    version_id: Identifier = Field(description='Immutable project version ID; version: prefix.')
    analysis_id: Identifier = Field(description='Analysis ID; analysis: prefix; fresh for a repeat analysis.')
    run_id: Identifier = Field(description='Execution run ID; run: prefix; never reused for a retry.')
    source_revision: GitRevision = Field(description='Git object SHA-1 of the source, not a file SHA-256.')
    baseline_sha256: Sha256 = Field(description='SHA-256 of the immutable source manifest bytes.')

    @model_validator(mode='after')
    def typed_ids(self):
        for name, prefix in [('project_id', 'project:'), ('version_id', 'version:'),
                             ('analysis_id', 'analysis:'), ('run_id', 'run:')]:
            if not getattr(self, name).startswith(prefix):
                raise ValueError('scope identifier has the wrong entity prefix')
        return self


class Confidence(ContractModel):
    """Producer-reported confidence, not an automatically calibrated probability."""
    value: Annotated[float, Field(ge=0, le=1)] | None = Field(description='Normalized confidence or explicit null.')
    reason: Text | None = Field(description='Required when confidence is unknown; otherwise null.')

    @model_validator(mode='after')
    def explicit_unknown(self):
        unknown(self.value, self.reason, 'confidence')
        return self


class ToolProvenance(ContractModel):
    """Actual tool/version/config lineage; unavailable values stay unknown."""
    tool_id: Text = Field(description='Tool product or adapter identity.')
    version: Text | None = Field(description='Observed tool version; null if unknown.')
    version_reason: Text | None = Field(description='Why the version is unknown, or null when known.')
    config_sha256: Sha256 | None = Field(description='Actual configuration fingerprint, never an invented default.')
    config_reason: Text | None = Field(description='Why configuration is unavailable, or null when known.')

    @model_validator(mode='after')
    def explicit_unknown(self):
        unknown(self.version, self.version_reason, 'tool version')
        unknown(self.config_sha256, self.config_reason, 'tool configuration')
        return self


class ModelProvenance(ContractModel):
    """Provider/model attribution without guessing deployment or generation settings."""
    provider: Text = Field(description='Provider identity; local providers are allowed.')
    model: Text = Field(description='Reported model name; not proof that an integration exists.')
    revision: Text | None = Field(description='Exact observed model revision, or null.')
    revision_reason: Text | None = Field(description='Why the exact revision is unknown, or null.')
    settings: dict[Text, Text | int | float | bool | None] | None = Field(description='Observed non-secret generation settings, or null.')
    settings_reason: Text | None = Field(description='Why settings are unknown, or null when known.')

    @model_validator(mode='after')
    def explicit_unknown(self):
        unknown(self.revision, self.revision_reason, 'model revision')
        unknown(self.settings, self.settings_reason, 'model settings')
        sensitive = {'apikey', 'accesstoken', 'authtoken', 'authorization', 'password',
                     'secret', 'credential', 'credentials', 'privatekey', 'token'}
        if self.settings is not None and any(re.sub(r'[^a-z]', '', key.casefold()) in sensitive for key in self.settings):
            raise ValueError('model provenance must not contain credentials')
        return self


class Record(ContractModel):
    schema_version: Literal['1.0.0'] = Field(description='Exact supported contract version. Unknown versions are rejected.')
    id: Identifier = Field(description='Globally unique, type-prefixed immutable entity ID.')
    scope: Scope = Field(description='Source/project/version/analysis/run binding.')
    subject_sha256: Sha256 = Field(description='Actual observed source-manifest snapshot; baseline and candidate evidence must not be interchanged.')
    recorded_at: UtcTimestamp = Field(description='Actual UTC record timestamp; fixtures use an explicitly synthetic fixed timestamp.')


class Artifact(ContractModel):
    """Content-addressed opaque artifact reference; no local path or raw secret content."""
    id: Identifier = Field(description='artifact: identifier resolved by the future authorized artifact service.')
    sha256: Sha256 = Field(description='SHA-256 of actual artifact bytes, distinct from a Git object ID.')
    media_type: Text = Field(description='Artifact MIME type.')
    redaction: RedactionStatus = Field(description='Masking/review status; not a claim of scanner success.')


class FileIdentity(ContractModel):
    """Trusted input manifest entry; candidate metadata cannot redefine this policy."""
    id: Identifier = Field(description='file: identity of one source file in the snapshot.')
    path: PathValue = Field(description='Canonical repository-relative path, with forward slashes.')
    sha256: Sha256 = Field(description='SHA-256 of the original file bytes.')
    subject_sha256: Sha256 = Field(description='Manifest snapshot that owns this file identity.')
    is_symlink: bool = Field(description='True for a linked entry; never eligible as a patch target.')
    frozen: bool = Field(description='Trusted immutable/frozen artifact flag.')
    protected_test: bool = Field(description='Trusted frozen or protected test flag.')


class TestSuite(ContractModel):
    """Frozen test identity, separate from a particular test execution."""
    id: Identifier = Field(description='suite: immutable baseline test-suite identifier.')
    sha256: Sha256 = Field(description='SHA-256 of the frozen test-suite manifest bytes.')
    case_ids: list[Identifier] = Field(description='Stable case: identifiers, including failed cases.')


class Attempt(ContractModel):
    """Failure-inclusive denominator ledger; not a worker implementation."""
    id: Identifier = Field(description='attempt: identifier; never erased after failure.')
    job_id: Identifier = Field(description='job: parent refactoring job.')
    number: Annotated[int, Field(ge=1, le=3)] = Field(description='One initial candidate plus at most two corrections.')
    started: bool = Field(description='Whether this planned attempt actually started.')
    execution_status: ExecutionStatus = Field(description='Execution outcome, independent of behavioral and quality results.')
    reason: Text | None = Field(description='Failure/unavailable/not-run explanation, or null after completion.')
    failure_kind: Literal['PROVIDER_ERROR', 'TIMEOUT', 'COMPILATION_FAILURE', 'TEST_FAILURE', 'SECURITY_REJECTION',
                          'CONFLICT_REJECTION', 'CANCELLED', 'ENVIRONMENT_BLOCKER', 'CONTRACT_REJECTION'] | None = Field(description='Explicit failure category, or null for completed/not-yet-failed work.')
    evidence_ids: list[Identifier] = Field(description='evidence: references retaining the failure or actual attempt outcome.')
    artifact_ids: list[Identifier] = Field(description='artifact: redacted failure/raw-rejection receipts; invalid proposals need not be admitted as valid PatchCandidates.')


class SourceLocation(Record):
    """1-based lines and Unicode-scalar columns; range end is exclusive."""
    kind: Literal['SourceLocation']
    path: PathValue | None = Field(description='Portable source path; null only for an unresolved location.')
    file_id: Identifier | None = Field(description='file: reference, or null when unresolved.')
    file_sha256: Sha256 | None = Field(description='Original source-file SHA-256, or null when unresolved.')
    resolution: Literal['RESOLVED', 'UNRESOLVED']
    reason: Text | None = Field(description='Explicit unresolved reason, otherwise null.')
    start_line: Annotated[int, Field(ge=1)] | None
    start_column: Annotated[int, Field(ge=1)] | None
    end_line: Annotated[int, Field(ge=1)] | None
    end_column: Annotated[int, Field(ge=1)] | None
    symbol_id: Identifier | None = Field(description='Optional symbol: reference; null means no resolved symbol.')

    @model_validator(mode='after')
    def valid_range(self):
        coordinates = (self.start_line, self.start_column, self.end_line, self.end_column)
        if self.resolution == 'RESOLVED':
            if any(value is None for value in (*coordinates, self.path, self.file_id, self.file_sha256)) or self.reason is not None:
                raise ValueError('resolved location requires source identity and all coordinates')
            if (self.end_line, self.end_column) <= (self.start_line, self.start_column):
                raise ValueError('exclusive range end must follow start')
        elif any(value is not None for value in coordinates) or not self.reason:
            raise ValueError('unresolved coordinates must be null with an explicit reason')
        return self


class Symbol(Record):
    """Language-independent symbol identity with explicit resolution uncertainty."""
    kind: Literal['Symbol']
    language: Language
    name: Text
    signature: Text | None
    location_id: Identifier
    resolution: Literal['RESOLVED', 'UNRESOLVED']
    reason: Text | None
    public_api: bool | None = Field(description='Null means visibility is unknown; it is not equivalent to private.')
    evidence_ids: list[Identifier]


class DependencyEdge(Record):
    """Observed or unresolved symbol relationship; unknown edges remain visible."""
    kind: Literal['DependencyEdge']
    from_symbol_id: Identifier
    to_symbol_id: Identifier | None
    relationship: Literal['CALL', 'READ', 'WRITE', 'IMPORT', 'INHERIT', 'UNKNOWN']
    resolution: Literal['RESOLVED', 'UNRESOLVED']
    reason: Text | None
    evidence_ids: list[Identifier]

    @model_validator(mode='after')
    def target_state(self):
        if self.resolution == 'RESOLVED' and (self.to_symbol_id is None or self.reason is not None):
            raise ValueError('resolved dependency requires a target and no unresolved reason')
        if self.resolution == 'UNRESOLVED' and not self.reason:
            raise ValueError('unresolved dependency requires a reason')
        return self


class Evidence(Record):
    """Attributable evidence; an LLM claim is never independent verified evidence."""
    kind: Literal['Evidence']
    producer_kind: Literal['DETERMINISTIC_TOOL', 'HUMAN', 'LLM']
    actor_id: Identifier | None = Field(description='actor: authenticated human reviewer identity for HUMAN evidence; otherwise null.')
    tool: ToolProvenance
    rule_id: Text | None
    model: ModelProvenance | None
    artifact_id: Identifier
    location_ids: list[Identifier]
    symbol_ids: list[Identifier]
    verification: Literal['VERIFIED', 'UNCONFIRMED', 'REJECTED', 'UNAVAILABLE']
    confidence: Confidence
    redaction: RedactionStatus

    @model_validator(mode='after')
    def llm_is_not_verification(self):
        if ((self.producer_kind == 'HUMAN') != (self.actor_id is not None)
                or self.actor_id is not None and not self.actor_id.startswith('actor:')):
            raise ValueError('human evidence requires its actual actor identity')
        if self.producer_kind == 'LLM' and (self.model is None or self.verification == 'VERIFIED'):
            raise ValueError('LLM claims need model provenance and cannot independently be VERIFIED')
        if self.producer_kind != 'LLM' and self.model is not None:
            raise ValueError('model provenance is reserved for model-generated claims')
        return self


class Finding(Record):
    """Normalized quality/security/baseline observation with stable rule and evidence lineage."""
    kind: Literal['Finding']
    classification: Literal['QUALITY_REFACTOR', 'SECURITY_REVIEW', 'BASELINE']
    category: Literal['QUALITY', 'COMPLEXITY', 'DUPLICATION', 'SECURITY', 'BASELINE']
    rule_id: Text
    tool: ToolProvenance
    location_ids: Annotated[list[Identifier], Field(min_length=1)]
    evidence_ids: Annotated[list[Identifier], Field(min_length=1)]
    confidence: Confidence
    eligibility: Literal['ELIGIBLE', 'INELIGIBLE', 'UNRESOLVED']
    eligibility_reason: Text | None
    status: Literal['OPEN', 'RESOLVED', 'SUPPRESSED', 'UNVERIFIED']

    @model_validator(mode='after')
    def classification_gate(self):
        if self.classification != 'QUALITY_REFACTOR' and self.eligibility == 'ELIGIBLE':
            raise ValueError('only QUALITY_REFACTOR findings can be eligible')
        if (self.classification == 'SECURITY_REVIEW') != (self.category == 'SECURITY'):
            raise ValueError('security classification and category must agree')
        if (self.classification == 'BASELINE') != (self.category == 'BASELINE'):
            raise ValueError('baseline classification and category must agree')
        if self.eligibility != 'ELIGIBLE' and not self.eligibility_reason:
            raise ValueError('ineligible or unresolved finding requires an explanation')
        if self.category == 'DUPLICATION' and len(self.location_ids) < 2:
            raise ValueError('duplication requires both source locations')
        return self


class ComparisonContext(ContractModel):
    """Explicit reproducibility inputs behind a metric comparison fingerprint."""
    tool: ToolProvenance
    rule_set_version: Text | None = Field(description='Observed ruleset/metric definition version; null if unknown.')
    rule_set_reason: Text | None = Field(description='Why the ruleset version is unknown; otherwise null.')
    measurement_scope_sha256: Sha256 = Field(description='Fingerprint of the same target files/symbols/measurement definition, not their changing contents.')
    environment_sha256: Sha256 | None = Field(description='Observed execution environment fingerprint, or null.')
    environment_reason: Text | None = Field(description='Why the environment fingerprint is unknown; otherwise null.')
    test_suite_sha256: Sha256 | None = Field(description='Frozen suite fingerprint for test/coverage comparisons; null when not applicable or unknown.')
    test_suite_state: Literal['KNOWN', 'NOT_APPLICABLE', 'UNKNOWN'] = Field(description='Distinguishes an inapplicable suite from missing comparison context.')

    @model_validator(mode='after')
    def explicit_context(self):
        unknown(self.rule_set_version, self.rule_set_reason, 'rule set version')
        unknown(self.environment_sha256, self.environment_reason, 'comparison environment')
        if (self.test_suite_state == 'KNOWN') != (self.test_suite_sha256 is not None):
            raise ValueError('test suite comparison state and fingerprint disagree')
        return self


class Metric(Record):
    """Measured quantity with comparison fingerprint and failure-inclusive population."""
    kind: Literal['Metric']
    name: Text
    unit: Literal['COUNT', 'PERCENT', 'MILLISECONDS', 'TOKENS', 'CURRENCY']
    currency_code: Annotated[str, Field(pattern=r'^[A-Z]{3}$')] | None = Field(description='Explicit ISO-style three-letter currency code for CURRENCY, otherwise null; never inferred from a provider name.')
    phase: Literal['BASELINE', 'CANDIDATE']
    value: Annotated[float, Field(ge=0)] | None
    measurement: Literal['MEASURED', 'UNKNOWN', 'UNAVAILABLE', 'NOT_APPLICABLE']
    reason: Text | None
    comparison_key: Sha256 = Field(description='Fingerprint of tool/rules/config/measurement scope; excludes measured value.')
    comparison: ComparisonContext = Field(description='Actual comparable inputs; comparison_key is checked against these fields, not trusted as an opaque claim.')
    direction: Literal['LOWER_IS_BETTER', 'HIGHER_IS_BETTER', 'CONTEXTUAL']
    population: Literal['NONE', 'STARTED_ATTEMPTS', 'PLANNED_ATTEMPTS']
    denominator: Annotated[int, Field(ge=0)] | None
    attempt_ids: list[Identifier]
    evidence_ids: list[Identifier]

    @model_validator(mode='after')
    def measured_state(self):
        if self.measurement == 'MEASURED':
            if self.value is None or self.reason is not None or not self.evidence_ids:
                raise ValueError('measurement requires an actual value and evidence')
        elif self.value is not None or not self.reason:
            raise ValueError('unmeasured metric must be null with a reason')
        if self.unit == 'PERCENT' and self.value is not None and self.value > 100:
            raise ValueError('percent must be in [0, 100]')
        if self.denominator == 0 and self.value is not None:
            raise ValueError('zero denominator is N/A, not measured zero')
        if self.unit in ('COUNT', 'TOKENS') and self.value is not None and not self.value.is_integer():
            raise ValueError('count and token quantities must be whole numbers')
        if (self.unit == 'CURRENCY') != (self.currency_code is not None):
            raise ValueError('currency amounts require their own explicit currency code')
        return self


class TestResult(Record):
    """One actual frozen-suite execution; a build is not a test result."""
    kind: Literal['TestResult']
    suite_id: Identifier
    suite_sha256: Sha256
    tool: ToolProvenance
    environment_sha256: Sha256 | None
    execution_status: ExecutionStatus
    outcome: Literal['PASSED', 'FAILED', 'UNVERIFIED']
    total: Annotated[int, Field(ge=0)] | None
    passed: Annotated[int, Field(ge=0)] | None
    failed: Annotated[int, Field(ge=0)] | None
    skipped: Annotated[int, Field(ge=0)] | None
    reason: Text | None
    evidence_ids: list[Identifier]

    @model_validator(mode='after')
    def real_test_counts(self):
        counts = (self.total, self.passed, self.failed, self.skipped)
        if self.execution_status == 'COMPLETED':
            if any(x is None for x in counts) or self.total != self.passed + self.failed + self.skipped:
                raise ValueError('completed execution requires consistent test counts')
            if not self.evidence_ids or self.environment_sha256 is None:
                raise ValueError('completed execution requires evidence and environment')
        elif self.outcome == 'PASSED' or not self.reason:
            raise ValueError('incomplete execution cannot pass and requires a reason')
        if self.outcome == 'PASSED' and (self.execution_status != 'COMPLETED' or not self.total or self.failed or self.skipped):
            raise ValueError('PASSED requires a nonempty completed suite without failures/skips')
        if self.outcome == 'FAILED' and (self.failed is None or self.failed == 0):
            raise ValueError('failed test outcome requires an actually observed failing case')
        return self


class ToolchainRequirement(ContractModel):
    """Observed availability and version of a required toolchain component."""
    name: Text
    version: Text | None
    status: Literal['AVAILABLE', 'UNAVAILABLE', 'UNRESOLVED']
    reason: Text | None


class Capability(Record):
    """One language/component capability; parser support implies no other support."""
    kind: Literal['Capability']
    language: Language
    component_id: Identifier
    capability: CapabilityName
    status: Literal['SUPPORTED', 'UNSUPPORTED', 'UNAVAILABLE', 'UNRESOLVED', 'NOT_IMPLEMENTED']
    confidence: Confidence
    tool: ToolProvenance | None
    toolchain: list[ToolchainRequirement]
    evidence_ids: list[Identifier]
    limitations: list[Text]
    reason: Text | None

    @model_validator(mode='after')
    def supported_is_evidenced(self):
        if self.status == 'SUPPORTED':
            if not self.evidence_ids or self.tool is None or self.tool.version is None or not self.toolchain:
                raise ValueError('supported capability requires actual tool/version/toolchain evidence')
            if any(t.status != 'AVAILABLE' or t.version is None for t in self.toolchain):
                raise ValueError('unavailable or unknown toolchain cannot support a capability')
        elif not self.reason:
            raise ValueError('unsupported/unavailable/unresolved capability requires a reason')
        return self


class LanguageAdapterCapabilities(Record):
    """Shared adapter declaration, independently covering all nine capability dimensions."""
    kind: Literal['LanguageAdapterCapabilities']
    adapter_id: Identifier
    language: Language
    component_id: Identifier
    implementation_state: Literal['CONTRACT_DEFINED', 'RUNTIME_IMPLEMENTED']
    capability_ids: Annotated[list[Identifier], Field(min_length=9, max_length=9)]


class FindingSnapshot(ContractModel):
    """Immutable complete-Finding fingerprint recorded by Gate 1."""
    finding_id: Identifier
    fingerprint: Sha256 = Field(description='SHA-256 of canonical JSON of the complete selected Finding record.')


class IssueSelection(Record):
    """Approval Gate 1: immutable, source-bound selection snapshot, not an approval service."""
    kind: Literal['IssueSelection']
    selected_finding_ids: Annotated[list[Identifier], Field(min_length=1)]
    baseline_test_result_ids: Annotated[list[Identifier], Field(min_length=1)]
    snapshots: Annotated[list[FindingSnapshot], Field(min_length=1)]
    fingerprint: Sha256 = Field(description='Canonical scope+sorted snapshot fingerprint; excludes this field itself.')
    actor_id: Identifier
    created_at: UtcTimestamp
    approval_ref: Identifier
    eligibility: Literal['ELIGIBLE', 'REJECTED', 'UNRESOLVED']
    reasons: list[Text]


class ContextBudget(ContractModel):
    """Request-specific token bound and honest measured/unknown token usage."""
    max_tokens: Annotated[int, Field(ge=1)]
    used_tokens: Annotated[int, Field(ge=0)] | None
    measurement: Literal['MEASURED', 'UNKNOWN']
    reason: Text | None

    @model_validator(mode='after')
    def explicit_token_usage(self):
        unknown(self.used_tokens, self.reason, 'token usage')
        if (self.measurement == 'MEASURED') != (self.used_tokens is not None):
            raise ValueError('token measurement status and count disagree')
        return self


class ContextExclusion(ContractModel):
    """A deliberately excluded context reference and its reason."""
    reference_id: Identifier
    reason: Text


class ContextPackage(Record):
    """Bounded reference-only context; sensitive raw source is not a contract field."""
    kind: Literal['ContextPackage']
    selection_id: Identifier
    target_finding_id: Identifier
    target_symbol_id: Identifier | None
    source_location_ids: list[Identifier]
    caller_symbol_ids: list[Identifier]
    callee_symbol_ids: list[Identifier]
    dependency_ids: list[Identifier]
    test_result_ids: list[Identifier]
    public_api_symbol_ids: list[Identifier]
    known_side_effects: list[Text]
    side_effect_status: Literal['KNOWN', 'UNKNOWN']
    budget: ContextBudget
    included_ids: list[Identifier]
    excluded: list[ContextExclusion]
    missing_critical_ids: list[Identifier]
    unresolved_dependency_ids: list[Identifier]
    artifact_ids: list[Identifier]
    redaction: RedactionStatus
    evidence_ids: list[Identifier]
    completeness: Literal['COMPLETE', 'INCOMPLETE']
    reasons: list[Text]

    @model_validator(mode='after')
    def missing_context_is_not_complete(self):
        if self.completeness == 'COMPLETE':
            if (self.missing_critical_ids or self.unresolved_dependency_ids or self.target_symbol_id is None
                    or self.side_effect_status != 'KNOWN' or self.budget.used_tokens is None
                    or self.budget.used_tokens > self.budget.max_tokens
                    or self.redaction not in ('MASKED', 'NO_SENSITIVE_CONTENT')):
                raise ValueError('complete context requires bounded, resolved, reviewed critical context')
        elif not self.reasons:
            raise ValueError('incomplete context requires explicit reasons')
        return self


class ChangedFile(ContractModel):
    """One portable source file operation with explicit before/after integrity metadata."""
    file_id: Identifier
    path: PathValue
    operation: Literal['ADD', 'MODIFY', 'DELETE']
    before_sha256: Sha256 | None
    after_sha256: Sha256 | None

    @model_validator(mode='after')
    def consistent_operation(self):
        if (self.operation == 'ADD' and (self.before_sha256 is not None or self.after_sha256 is None)
                or self.operation == 'DELETE' and (self.before_sha256 is None or self.after_sha256 is not None)
                or self.operation == 'MODIFY' and (self.before_sha256 is None or self.after_sha256 is None)):
            raise ValueError('changed-file operation and hashes disagree')
        return self


class PatchCandidate(Record):
    """Proposed derivative patch metadata; never applies a patch or changes V0."""
    kind: Literal['PatchCandidate']
    job_id: Identifier
    attempt_id: Identifier
    selection_id: Identifier
    target_finding_id: Identifier
    technique: Text
    diff_artifact_id: Identifier
    diff_sha256: Sha256
    output_snapshot_sha256: Sha256 | None = Field(description='Observed candidate source-manifest hash; null before materialization.')
    output_manifest_artifact_id: Identifier | None
    output_snapshot_reason: Text | None
    allowed_paths: Annotated[list[ScopePath], Field(min_length=1)]
    changed_files: Annotated[list[ChangedFile], Field(min_length=1)]
    model: ModelProvenance
    validation_ids: list[Identifier]
    security_finding_ids: list[Identifier]
    security_status: SecurityStatus
    behavior_status: BehaviorStatus
    quality_outcome: QualityOutcome
    applicability: Literal['APPLICABLE', 'REJECTED', 'UNVERIFIED']
    rejection_reasons: list[Text]
    confidence: Confidence

    @model_validator(mode='after')
    def rejected_has_reason(self):
        unknown(self.output_snapshot_sha256, self.output_snapshot_reason, 'candidate snapshot')
        if (self.output_snapshot_sha256 is None) != (self.output_manifest_artifact_id is None):
            raise ValueError('candidate snapshot and manifest reference must be known together')
        if self.applicability != 'APPLICABLE' and not self.rejection_reasons:
            raise ValueError('rejected/unverified patch requires reasons')
        if self.security_status == 'FINDINGS' and not self.security_finding_ids:
            raise ValueError('security FINDINGS requires referenced findings')
        if self.security_status == 'CLEAN' and self.security_finding_ids:
            raise ValueError('CLEAN cannot conceal security findings')
        return self


class ValidationResult(Record):
    """Evidence-backed independent behavior, quality, security and execution dimensions."""
    kind: Literal['ValidationResult']
    candidate_ids: Annotated[list[Identifier], Field(min_length=1)]
    validation_scope: Literal['CANDIDATE', 'COMBINED']
    workspace_kind: Literal['CANDIDATE_DERIVATIVE', 'FRESH_V0_COMBINATION']
    workspace_manifest_artifact_id: Identifier
    execution_status: ExecutionStatus
    build_status: BehaviorStatus
    behavior_status: BehaviorStatus
    behavior_reason: Text | None
    quality_outcome: QualityOutcome
    quality_reason: Text | None
    security_status: SecurityStatus
    security_reason: Text | None
    security_execution_status: ExecutionStatus
    security_evidence_ids: list[Identifier]
    security_finding_ids: list[Identifier]
    test_result_ids: list[Identifier]
    metric_ids: list[Identifier]
    evidence_ids: list[Identifier]
    reason: Text | None

    @model_validator(mode='after')
    def independent_evidence_states(self):
        if (self.validation_scope == 'CANDIDATE' and (len(self.candidate_ids) != 1 or self.workspace_kind != 'CANDIDATE_DERIVATIVE')
                or self.validation_scope == 'COMBINED' and self.workspace_kind != 'FRESH_V0_COMBINATION'):
            raise ValueError('individual and combined validation need their own workspace kind')
        if self.behavior_status == 'UNVERIFIED' and not self.behavior_reason:
            raise ValueError('unverified behavior requires an explicit reason')
        if self.quality_outcome == 'NOT_COMPARABLE' and not self.quality_reason:
            raise ValueError('incomparable quality requires an explicit reason')
        if self.security_status in ('NOT_RUN', 'UNAVAILABLE', 'INCOMPLETE') and not self.security_reason:
            raise ValueError('unverified security requires an explicit reason')
        if self.execution_status != 'COMPLETED' and (self.behavior_status == 'PASSED' or not self.reason):
            raise ValueError('incomplete validation cannot establish behavioral PASS')
        if self.security_status in ('CLEAN', 'FINDINGS') and (
                self.security_execution_status != 'COMPLETED' or not self.security_evidence_ids):
            raise ValueError('successful security assessment requires a completed scan and evidence')
        if self.security_status == 'CLEAN' and self.security_finding_ids:
            raise ValueError('CLEAN security cannot contain security findings')
        if self.security_status == 'FINDINGS' and not self.security_finding_ids:
            raise ValueError('FINDINGS security requires referenced findings')
        if self.behavior_status == 'PASSED' and not self.test_result_ids:
            raise ValueError('build-only validation cannot establish behavioral PASS')
        if self.quality_outcome != 'NOT_COMPARABLE' and not self.metric_ids:
            raise ValueError('quality assessment requires actual comparison metrics')
        return self


Entity = Annotated[Union[SourceLocation, Symbol, DependencyEdge, Evidence, Finding, Metric,
                         TestResult, Capability, LanguageAdapterCapabilities, IssueSelection,
                         ContextPackage, PatchCandidate, ValidationResult], Field(discriminator='kind')]


class ContractBundle(ContractModel):
    """Closed reference graph for validation gates; standalone records validate only their shape."""
    schema_version: Literal['1.0.0']
    mode: Literal['FIXTURE', 'INTERCHANGE'] = Field(description='FIXTURE examples do not claim real tool/model execution.')
    scope: Scope
    files: list[FileIdentity]
    artifacts: list[Artifact]
    test_suites: list[TestSuite]
    attempts: list[Attempt]
    records: Annotated[list[Entity], Field(min_length=1)]


class ResultEnvelope(ContractModel):
    """Versioned successful API result; references are validated as a closed graph."""
    schema_version: Literal['1.0.0']
    request_id: Identifier
    status: Literal['OK']
    data: ContractBundle
    next_cursor: Text | None = Field(description='Opaque cursor; null means no additional page.')


class ErrorDetail(ContractModel):
    """Safe structured failure metadata without reflecting raw inputs."""
    entity_id: Identifier | None
    field: Text | None


class ErrorEnvelope(ContractModel):
    """Safe API error without raw source, stack trace, credentials or host filesystem paths."""
    schema_version: Literal['1.0.0']
    request_id: Identifier
    status: Literal['ERROR']
    code: Literal['INVALID_CONTRACT', 'BROKEN_REFERENCE', 'SCOPE_MISMATCH', 'STALE_SELECTION',
                  'FORBIDDEN_SCOPE', 'UNAVAILABLE_CAPABILITY', 'INCOMPLETE_CONTEXT',
                  'VALIDATION_FAILED', 'INTERNAL_ERROR']
    component: Literal['API', 'CONTRACT', 'ADAPTER', 'CONTEXT', 'VALIDATION']
    message: Text = Field(description='Static safe user message; never reflect raw validation input.')
    retryable: bool
    details: list[ErrorDetail]


class AdapterRequest(ContractModel):
    """One explicitly routed, bounded operation; no parser-implies-test assumption."""
    schema_version: Literal['1.0.0']
    scope: Scope
    language: Language
    component_id: Identifier
    adapter_capabilities_id: Identifier
    capability_id: Identifier
    operation: CapabilityName
    input_artifact_id: Identifier
    timeout_seconds: Annotated[int, Field(ge=1, le=3600)]


class AdapterResult(ContractModel):
    """Execution status remains distinct from behavioral, quality and security evidence."""
    schema_version: Literal['1.0.0']
    operation: CapabilityName
    execution_status: ExecutionStatus
    result: ResultEnvelope | ErrorEnvelope
