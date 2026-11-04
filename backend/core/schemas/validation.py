"""Referential and safety semantics for data interchange, not tool execution.

PatchPolicy is supplied by the trusted consumer. A patch cannot authorize its own
paths, declare its own current baseline, or overwrite frozen test/source policy.
"""
import hashlib
from dataclasses import dataclass

import rfc8785
from pydantic import ValidationError

from .models import (CAPABILITIES, Capability, ContextPackage, ContractBundle, DependencyEdge, FileIdentity, Scope, TestSuite,
                     ErrorEnvelope, Evidence, Finding, IssueSelection, LanguageAdapterCapabilities,
                     Metric, PatchCandidate, SourceLocation, Symbol, TestResult, ValidationResult)

PREFIXES = {
    'SourceLocation': 'location', 'Symbol': 'symbol', 'DependencyEdge': 'dependency',
    'Evidence': 'evidence', 'Finding': 'finding', 'Metric': 'metric', 'TestResult': 'test',
    'Capability': 'capability', 'LanguageAdapterCapabilities': 'adaptercaps',
    'IssueSelection': 'selection', 'ContextPackage': 'context', 'PatchCandidate': 'patch',
    'ValidationResult': 'validation',
}
MESSAGES = {
    'INVALID_CONTRACT': 'The payload does not satisfy the supported contract.',
    'BROKEN_REFERENCE': 'A required entity reference is missing, duplicated or inconsistent.',
    'SCOPE_MISMATCH': 'The payload refers to a different project, source version or analysis.',
    'STALE_SELECTION': 'The selected findings have changed. A fresh selection is required.',
    'FORBIDDEN_SCOPE': 'The proposed patch violates the trusted file policy.',
    'UNAVAILABLE_CAPABILITY': 'The requested capability is not supported by verified evidence.',
    'INCOMPLETE_CONTEXT': 'Critical context is missing, unresolved, unreviewed or outside its budget.',
    'VALIDATION_FAILED': 'The claimed result is not supported by the referenced validation evidence.',
    'INTERNAL_ERROR': 'The request could not be completed.',
}


class ContractViolation(ValueError):
    """Safe stable error; never copies raw source, Pydantic inputs or local paths."""
    def __init__(self, code, field=None):
        self.code = code
        self.field = field
        super().__init__(MESSAGES[code])

    def envelope(self, request_id='request:unresolved'):
        return ErrorEnvelope(schema_version='1.0.0', request_id=request_id, status='ERROR',
                             code=self.code, component='CONTRACT', message=MESSAGES[self.code],
                             retryable=self.code in ('STALE_SELECTION', 'UNAVAILABLE_CAPABILITY'),
                             details=[dict(entity_id=None, field=self.field)]).model_dump(mode='json')


def check(condition, code='BROKEN_REFERENCE', field=None):
    if not condition:
        raise ContractViolation(code, field)


def canonical_sha256(value):
    """SHA-256 of RFC 8785/JCS bytes, shared by Python, browser and native consumers."""
    return hashlib.sha256(rfc8785.dumps(value)).hexdigest()


def finding_fingerprint(finding):
    """Fingerprint immutable selection-relevant Finding fields, including source and evidence IDs."""
    data = finding.model_dump(mode='json') if isinstance(finding, Finding) else finding
    return canonical_sha256(data)


def selection_fingerprint(scope, snapshots):
    scope = scope.model_dump(mode='json') if hasattr(scope, 'model_dump') else scope
    rows = [item.model_dump(mode='json') if hasattr(item, 'model_dump') else item for item in snapshots]
    return canonical_sha256(dict(scope=scope, snapshots=sorted(rows, key=lambda item: item['finding_id'])))


def metric_comparison_key(metric):
    data = metric.model_dump(mode='json') if isinstance(metric, Metric) else metric
    return canonical_sha256({key: data[key] for key in ('name', 'unit', 'currency_code', 'direction', 'comparison')})


@dataclass(frozen=True)
class PatchPolicy:
    """Trusted caller input, deliberately excluded from the candidate wire model."""
    expected_scope: Scope
    allowed_paths: tuple[str, ...]
    expected_files: tuple[FileIdentity, ...]
    expected_test_suites: tuple[TestSuite, ...]
    protected_paths: tuple[str, ...] = ('tests/', 'test/', 'experiments/original-ai-code/',
                                       'experiments/java-pilot/manifests/',
                                       'experiments/java-pilot/provenance/', '.github/', '.agents/')


def path_matches(path, scope):
    return any(path.startswith(item) if item.endswith('/') else path == item for item in scope)


def validate_bundle(payload, *, patch_policy=None):
    """Validate strict models then the closed graph. External stores authenticate artifact bytes.

A bundle containing a candidate requires an independently supplied PatchPolicy.
No file access, network, model inference, approval persistence or patch apply is
performed by this function.
"""
    try:
        bundle = (ContractBundle.model_validate_json(payload) if isinstance(payload, (str, bytes))
                  else ContractBundle.model_validate(payload))
    except ValidationError:
        raise ContractViolation('INVALID_CONTRACT') from None
    if patch_policy is not None:
        check(isinstance(patch_policy, PatchPolicy), 'FORBIDDEN_SCOPE', 'patch_policy')
        check(bundle.scope == patch_policy.expected_scope, 'SCOPE_MISMATCH', 'scope')
        check({file.id: file for file in bundle.files if file.subject_sha256 == bundle.scope.baseline_sha256}
              == {file.id: file for file in patch_policy.expected_files}, 'SCOPE_MISMATCH', 'files')
        check({suite.id: suite for suite in bundle.test_suites}
              == {suite.id: suite for suite in patch_policy.expected_test_suites}, 'SCOPE_MISMATCH', 'test_suites')
    records = {}
    catalog = {}
    for collection, prefix in ((bundle.files, 'file'), (bundle.artifacts, 'artifact'),
                               (bundle.test_suites, 'suite'), (bundle.attempts, 'attempt')):
        for entry in collection:
            check(entry.id.startswith(prefix + ':') and entry.id not in catalog, field='id')
            catalog[entry.id] = entry
    for record in bundle.records:
        check(record.id.startswith(PREFIXES[record.kind] + ':') and record.id not in catalog, field='id')
        check(record.scope == bundle.scope, 'SCOPE_MISMATCH', 'scope')
        catalog[record.id] = record
        records[record.id] = record
    check(len({(file.subject_sha256, file.path.casefold()) for file in bundle.files}) == len(bundle.files),
          'FORBIDDEN_SCOPE', 'files')
    for suite in bundle.test_suites:
        check(len(set(suite.case_ids)) == len(suite.case_ids)
              and all(case.startswith('case:') for case in suite.case_ids), field='case_ids')
    for attempt in bundle.attempts:
        check(attempt.job_id.startswith('job:'), field='job_id')
        check(attempt.started or attempt.execution_status in ('NOT_RUN', 'UNAVAILABLE'),
              'VALIDATION_FAILED', 'attempts')
        check(attempt.execution_status == 'COMPLETED' or attempt.reason is not None,
              'VALIDATION_FAILED', 'attempts')
        check(not (attempt.started and attempt.execution_status == 'NOT_RUN'), 'VALIDATION_FAILED', 'attempts')
        check(all(isinstance(catalog.get(identifier), Evidence) for identifier in attempt.evidence_ids)
              and all(identifier.startswith('artifact:') and identifier in catalog for identifier in attempt.artifact_ids),
              field='attempts')
        if attempt.execution_status == 'FAILED':
            check(attempt.failure_kind is not None and (attempt.evidence_ids or attempt.artifact_ids),
                  'VALIDATION_FAILED', 'attempts')
        if attempt.execution_status == 'COMPLETED':
            check(attempt.failure_kind is None, 'VALIDATION_FAILED', 'failure_kind')
    attempt_keys = [(a.job_id, a.number) for a in bundle.attempts]
    check(len(set(attempt_keys)) == len(attempt_keys), field='attempts')

    def ref(identifier, expected=None):
        item = catalog.get(identifier)
        check(item is not None and (expected is None or isinstance(item, expected)), field='reference')
        return item

    def refs(identifiers, expected=None):
        check(len(identifiers) == len(set(identifiers)), field='references')
        return [ref(identifier, expected) for identifier in identifiers]

    def verified_evidence(identifiers, subject=None):
        items = refs(identifiers, Evidence)
        independent = [e for e in items if e.verification == 'VERIFIED' and e.producer_kind != 'LLM']
        check(independent,
              'VALIDATION_FAILED', 'evidence_ids')
        if subject is not None:
            check(all(e.subject_sha256 == subject for e in items), 'SCOPE_MISMATCH', 'subject_sha256')
        return independent

    for record in bundle.records:
        if isinstance(record, SourceLocation):
            if record.file_id is not None:
                file = ref(record.file_id)
                check(record.file_id.startswith('file:') and file.path == record.path
                      and file.sha256 == record.file_sha256 and file.subject_sha256 == record.subject_sha256,
                      'SCOPE_MISMATCH', 'file_id')
            if record.symbol_id is not None:
                ref(record.symbol_id, Symbol)
        elif isinstance(record, Symbol):
            location = ref(record.location_id, SourceLocation)
            check(location.subject_sha256 == record.subject_sha256, 'SCOPE_MISMATCH', 'location_id')
            check(record.resolution != 'RESOLVED' or location.resolution == 'RESOLVED', field='location_id')
            check(record.resolution != 'UNRESOLVED' or record.reason is not None, field='reason')
            refs(record.evidence_ids, Evidence)
        elif isinstance(record, DependencyEdge):
            check(ref(record.from_symbol_id, Symbol).subject_sha256 == record.subject_sha256,
                  'SCOPE_MISMATCH', 'from_symbol_id')
            if record.to_symbol_id is not None:
                check(ref(record.to_symbol_id, Symbol).subject_sha256 == record.subject_sha256,
                      'SCOPE_MISMATCH', 'to_symbol_id')
            refs(record.evidence_ids, Evidence)
        elif isinstance(record, Evidence):
            artifact = ref(record.artifact_id)
            check(record.artifact_id.startswith('artifact:') and artifact.redaction == record.redaction,
                  field='artifact_id')
            check(all(item.subject_sha256 == record.subject_sha256
                      for item in refs(record.location_ids, SourceLocation) + refs(record.symbol_ids, Symbol)),
                  'SCOPE_MISMATCH', 'source_references')
            check(record.verification != 'VERIFIED' or record.producer_kind == 'HUMAN' or record.tool.version is not None,
                  'VALIDATION_FAILED', 'tool.version')
        elif isinstance(record, Finding):
            locations = refs(record.location_ids, SourceLocation)
            evidence = refs(record.evidence_ids, Evidence)
            check(all(item.subject_sha256 == record.subject_sha256 for item in locations + evidence),
                  'SCOPE_MISMATCH', 'subject_sha256')
            evidenced_locations = set(location for e in evidence for location in e.location_ids)
            for e in evidence:
                evidenced_locations.update(ref(symbol, Symbol).location_id for symbol in e.symbol_ids)
            check(any(location.id in evidenced_locations for location in locations), field='evidence_ids')
            if record.eligibility == 'ELIGIBLE':
                verified_evidence(record.evidence_ids, record.subject_sha256)
                check(record.status == 'OPEN' and all(l.resolution == 'RESOLVED' for l in locations),
                      'VALIDATION_FAILED', 'eligibility')
        elif isinstance(record, Metric):
            refs(record.evidence_ids, Evidence)
            refs(record.attempt_ids)
            if record.measurement == 'MEASURED':
                proofs = verified_evidence(record.evidence_ids, record.subject_sha256)
                check(any(e.tool == record.comparison.tool for e in proofs), 'VALIDATION_FAILED', 'comparison.tool')
            check(record.comparison_key == metric_comparison_key(record), 'VALIDATION_FAILED', 'comparison_key')
            if record.phase == 'BASELINE':
                check(record.subject_sha256 == bundle.scope.baseline_sha256, 'SCOPE_MISMATCH', 'subject_sha256')
            if record.population != 'NONE':
                expected = {a.id for a in bundle.attempts if a.started or record.population == 'PLANNED_ATTEMPTS'}
                check(set(record.attempt_ids) == expected and record.denominator == len(expected),
                      'VALIDATION_FAILED', 'denominator')
            else:
                check(record.denominator is None and not record.attempt_ids, field='population')
        elif isinstance(record, TestResult):
            suite = ref(record.suite_id)
            check(record.suite_id.startswith('suite:') and suite.sha256 == record.suite_sha256,
                  'SCOPE_MISMATCH', 'suite_sha256')
            if record.execution_status == 'COMPLETED':
                check(record.total == len(suite.case_ids), 'VALIDATION_FAILED', 'total')
                proofs = verified_evidence(record.evidence_ids, record.subject_sha256)
                check(any(e.producer_kind == 'DETERMINISTIC_TOOL' and e.tool == record.tool for e in proofs),
                      'VALIDATION_FAILED', 'tool')
            else:
                refs(record.evidence_ids, Evidence)
        elif isinstance(record, Capability):
            if record.status == 'SUPPORTED':
                verified_evidence(record.evidence_ids)
            else:
                refs(record.evidence_ids, Evidence)
            check(record.component_id.startswith('component:'), field='component_id')
        elif isinstance(record, LanguageAdapterCapabilities):
            check(record.adapter_id.startswith('adapter:') and record.component_id.startswith('component:'), field='adapter_id')
            capabilities = refs(record.capability_ids, Capability)
            check({cap.capability for cap in capabilities} == set(CAPABILITIES)
                  and all(cap.language == record.language and cap.component_id == record.component_id
                          for cap in capabilities), 'UNAVAILABLE_CAPABILITY', 'capability_ids')
            if record.implementation_state == 'CONTRACT_DEFINED':
                check(not any(cap.status == 'SUPPORTED' for cap in capabilities),
                      'UNAVAILABLE_CAPABILITY', 'implementation_state')
            else:
                check(any(cap.status == 'SUPPORTED' for cap in capabilities),
                      'UNAVAILABLE_CAPABILITY', 'implementation_state')
        elif isinstance(record, IssueSelection):
            findings = refs(record.selected_finding_ids, Finding)
            baseline_tests = refs(record.baseline_test_result_ids, TestResult)
            check(record.subject_sha256 == bundle.scope.baseline_sha256
                  and all(item.subject_sha256 == record.subject_sha256 for item in findings + baseline_tests),
                  'SCOPE_MISMATCH', 'subject_sha256')
            check(record.actor_id.startswith('actor:') and record.approval_ref.startswith('approval:'),
                  field='approval_ref')
            snapshot_ids = [s.finding_id for s in record.snapshots]
            check(len(snapshot_ids) == len(set(snapshot_ids)) and set(snapshot_ids) == {f.id for f in findings},
                  'STALE_SELECTION', 'snapshots')
            for snapshot in record.snapshots:
                check(snapshot.fingerprint == finding_fingerprint(ref(snapshot.finding_id, Finding)),
                      'STALE_SELECTION', 'snapshots')
            check(record.fingerprint == selection_fingerprint(record.scope, record.snapshots),
                  'STALE_SELECTION', 'fingerprint')
            if record.eligibility == 'ELIGIBLE':
                check(isinstance(patch_policy, PatchPolicy), 'FORBIDDEN_SCOPE', 'trusted_baseline')
                check(all(f.classification == 'QUALITY_REFACTOR' and f.eligibility == 'ELIGIBLE'
                          and f.status == 'OPEN' for f in findings), 'VALIDATION_FAILED', 'selected_finding_ids')
                check(baseline_tests and all(test.outcome == 'PASSED' for test in baseline_tests),
                      'VALIDATION_FAILED', 'baseline_test_result_ids')
            else:
                check(record.reasons, 'VALIDATION_FAILED', 'reasons')
        elif isinstance(record, ContextPackage):
            selection = ref(record.selection_id, IssueSelection)
            finding = ref(record.target_finding_id, Finding)
            check(record.subject_sha256 == selection.subject_sha256 == finding.subject_sha256,
                  'SCOPE_MISMATCH', 'subject_sha256')
            check(finding.id in selection.selected_finding_ids, field='target_finding_id')
            if record.target_symbol_id is not None:
                target = ref(record.target_symbol_id, Symbol)
                check(target.location_id in finding.location_ids
                      or any(ref(location, SourceLocation).symbol_id == target.id for location in finding.location_ids),
                      field='target_symbol_id')
            for field, expected in [('source_location_ids', SourceLocation), ('caller_symbol_ids', Symbol),
                                    ('callee_symbol_ids', Symbol), ('dependency_ids', DependencyEdge),
                                    ('test_result_ids', TestResult), ('public_api_symbol_ids', Symbol)]:
                check(all(item.subject_sha256 == record.subject_sha256 for item in refs(getattr(record, field), expected)),
                      'SCOPE_MISMATCH', field)
            refs(record.included_ids)
            refs(record.evidence_ids, Evidence)
            artifacts = refs(record.artifact_ids)
            check(all(a.id.startswith('artifact:') for a in artifacts), field='artifact_ids')
            excluded_ids = [item.reference_id for item in record.excluded]
            check(len(set(excluded_ids)) == len(excluded_ids) and not set(excluded_ids) & set(record.included_ids),
                  field='excluded')
            if record.completeness == 'COMPLETE':
                verified_evidence(record.evidence_ids, record.subject_sha256)
                check(selection.eligibility == 'ELIGIBLE' and record.target_symbol_id is not None,
                      'INCOMPLETE_CONTEXT', 'selection_id')
                check(all(a.redaction in ('MASKED', 'NO_SENSITIVE_CONTENT') for a in artifacts),
                      'INCOMPLETE_CONTEXT', 'artifact_ids')
                check(all(ref(d, DependencyEdge).resolution == 'RESOLVED' for d in record.dependency_ids),
                      'INCOMPLETE_CONTEXT', 'dependency_ids')
                check(all(ref(s, Symbol).public_api is True for s in record.public_api_symbol_ids),
                      'INCOMPLETE_CONTEXT', 'public_api_symbol_ids')
                calls = {(ref(d, DependencyEdge).from_symbol_id, ref(d, DependencyEdge).to_symbol_id)
                         for d in record.dependency_ids if ref(d, DependencyEdge).relationship == 'CALL'}
                check(all((caller, record.target_symbol_id) in calls for caller in record.caller_symbol_ids)
                      and all((record.target_symbol_id, callee) in calls for callee in record.callee_symbol_ids),
                      'INCOMPLETE_CONTEXT', 'dependency_ids')
                critical = set(record.source_location_ids + record.caller_symbol_ids + record.callee_symbol_ids
                               + record.dependency_ids + record.test_result_ids + record.public_api_symbol_ids
                               + [record.target_finding_id, record.target_symbol_id])
                check(critical <= set(record.included_ids) and set(finding.location_ids) <= set(record.source_location_ids),
                      'INCOMPLETE_CONTEXT', 'included_ids')
        elif isinstance(record, PatchCandidate):
            check(isinstance(patch_policy, PatchPolicy), 'FORBIDDEN_SCOPE', 'patch_policy')
            check(record.subject_sha256 == bundle.scope.baseline_sha256, 'SCOPE_MISMATCH', 'subject_sha256')
            selection = ref(record.selection_id, IssueSelection)
            check(record.target_finding_id in selection.selected_finding_ids and selection.eligibility == 'ELIGIBLE',
                  'VALIDATION_FAILED', 'selection_id')
            attempt = ref(record.attempt_id)
            check(record.attempt_id.startswith('attempt:') and attempt.job_id == record.job_id and attempt.started,
                  field='attempt_id')
            artifact = ref(record.diff_artifact_id)
            check(record.diff_artifact_id.startswith('artifact:') and record.diff_sha256 == artifact.sha256,
                  'VALIDATION_FAILED', 'diff_sha256')
            if record.output_manifest_artifact_id is not None:
                output_manifest = ref(record.output_manifest_artifact_id)
                check(record.output_manifest_artifact_id.startswith('artifact:')
                      and output_manifest.sha256 == record.output_snapshot_sha256,
                      'SCOPE_MISMATCH', 'output_snapshot_sha256')
            changed = [file.path for file in record.changed_files]
            check(len(set(path.casefold() for path in changed)) == len(changed), 'FORBIDDEN_SCOPE', 'changed_files')
            for change in record.changed_files:
                file = ref(change.file_id)
                check(change.file_id.startswith('file:') and file.path == change.path
                      and not file.is_symlink and not file.frozen and not file.protected_test,
                      'FORBIDDEN_SCOPE', 'changed_files')
                check(path_matches(change.path, record.allowed_paths)
                      and path_matches(change.path, patch_policy.allowed_paths)
                      and not path_matches(change.path.casefold(), tuple(p.casefold() for p in patch_policy.protected_paths)),
                      'FORBIDDEN_SCOPE', 'changed_files')
                if change.operation == 'ADD':
                    check(file.subject_sha256 == record.output_snapshot_sha256 and file.sha256 == change.after_sha256
                          and not any(base.path.casefold() == change.path.casefold() for base in patch_policy.expected_files),
                          'FORBIDDEN_SCOPE', 'changed_files')
                else:
                    check(file.subject_sha256 == bundle.scope.baseline_sha256, 'SCOPE_MISMATCH', 'file_id')
                    check(change.before_sha256 == file.sha256, 'SCOPE_MISMATCH', 'before_sha256')
            validations = refs(record.validation_ids, ValidationResult)
            check(all(record.id in v.candidate_ids for v in validations), field='validation_ids')
            security_findings = refs(record.security_finding_ids, Finding)
            check(all(f.classification == 'SECURITY_REVIEW' for f in security_findings),
                  'VALIDATION_FAILED', 'security_finding_ids')
            if (record.applicability == 'APPLICABLE' or record.behavior_status != 'UNVERIFIED'
                    or record.quality_outcome != 'NOT_COMPARABLE' or record.security_status in ('CLEAN', 'FINDINGS')):
                individual = [v for v in validations if v.validation_scope == 'CANDIDATE']
                check(individual and record.output_snapshot_sha256 is not None,
                      'VALIDATION_FAILED', 'validation_ids')
                latest = individual[-1]
                check((record.behavior_status, record.quality_outcome, record.security_status)
                      == (latest.behavior_status, latest.quality_outcome, latest.security_status),
                      'VALIDATION_FAILED', 'validation_ids')
                check(set(record.security_finding_ids) == set(latest.security_finding_ids),
                      'VALIDATION_FAILED', 'security_finding_ids')
            if record.security_status == 'CLEAN':
                check(validations and any(v.security_status == 'CLEAN' for v in validations)
                      and not record.security_finding_ids, 'VALIDATION_FAILED', 'security_status')
        elif isinstance(record, ValidationResult):
            candidates = refs(record.candidate_ids, PatchCandidate)
            check(all(record.id in candidate.validation_ids for candidate in candidates), field='candidate_ids')
            manifest = ref(record.workspace_manifest_artifact_id)
            check(record.workspace_manifest_artifact_id.startswith('artifact:') and manifest.sha256 == record.subject_sha256,
                  'SCOPE_MISMATCH', 'workspace_manifest_artifact_id')
            if record.validation_scope == 'CANDIDATE':
                check(record.subject_sha256 == candidates[0].output_snapshot_sha256,
                      'SCOPE_MISMATCH', 'subject_sha256')
            refs(record.evidence_ids, Evidence)
            security_findings = refs(record.security_finding_ids, Finding)
            check(all(f.classification == 'SECURITY_REVIEW' and f.subject_sha256 == record.subject_sha256
                      for f in security_findings),
                  'VALIDATION_FAILED', 'security_finding_ids')
            tests = refs(record.test_result_ids, TestResult)
            check(all(test.subject_sha256 == record.subject_sha256 for test in tests),
                  'SCOPE_MISMATCH', 'test_result_ids')
            metrics = refs(record.metric_ids, Metric)
            if record.behavior_status == 'PASSED':
                check(tests and all(test.outcome == 'PASSED' for test in tests),
                      'VALIDATION_FAILED', 'behavior_status')
                verified_evidence(record.evidence_ids, record.subject_sha256)
            elif record.behavior_status == 'FAILED':
                check(any(test.outcome == 'FAILED' for test in tests),
                      'VALIDATION_FAILED', 'behavior_status')
                verified_evidence(record.evidence_ids, record.subject_sha256)
            if record.security_status in ('CLEAN', 'FINDINGS'):
                proofs = verified_evidence(record.security_evidence_ids, record.subject_sha256)
                check(any(e.producer_kind == 'DETERMINISTIC_TOOL' for e in proofs),
                      'VALIDATION_FAILED', 'security_evidence_ids')
            else:
                refs(record.security_evidence_ids, Evidence)
            if record.quality_outcome != 'NOT_COMPARABLE':
                grouped = {}
                for metric in metrics:
                    check(metric.measurement == 'MEASURED' and metric.direction != 'CONTEXTUAL',
                          'VALIDATION_FAILED', 'metric_ids')
                    context = metric.comparison
                    check(context.tool.version is not None and context.tool.config_sha256 is not None
                          and context.rule_set_version is not None and context.environment_sha256 is not None
                          and context.test_suite_state != 'UNKNOWN', 'VALIDATION_FAILED', 'comparison')
                    check(metric.subject_sha256 == (bundle.scope.baseline_sha256 if metric.phase == 'BASELINE'
                                                    else record.subject_sha256), 'SCOPE_MISMATCH', 'metric_ids')
                    key = (metric.name, metric.unit, metric.comparison_key, metric.direction)
                    phases = grouped.setdefault(key, {})
                    check(metric.phase not in phases, 'VALIDATION_FAILED', 'metric_ids')
                    phases[metric.phase] = metric
                check(grouped and all(set(pair) == {'BASELINE', 'CANDIDATE'} for pair in grouped.values()),
                      'VALIDATION_FAILED', 'metric_ids')
                deltas = [(pair['CANDIDATE'].value - pair['BASELINE'].value)
                          * (1 if pair['BASELINE'].direction == 'HIGHER_IS_BETTER' else -1)
                          for pair in grouped.values()]
                inferred = 'WORSE' if any(d < 0 for d in deltas) else 'IMPROVED' if any(d > 0 for d in deltas) else 'UNCHANGED'
                check(record.quality_outcome == inferred, 'VALIDATION_FAILED', 'quality_outcome')
    return bundle
