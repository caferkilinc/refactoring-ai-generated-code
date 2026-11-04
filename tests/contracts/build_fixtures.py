"""Deterministic, explicitly synthetic consumer fixtures; never evidence of tool execution."""
import copy
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from backend.core.schemas.models import CAPABILITIES, LANGUAGES
from backend.core.schemas.validation import finding_fingerprint, selection_fingerprint, metric_comparison_key

SOURCE_BYTES = '\tα😀x\r\nnext\n'.encode('utf-8')


def digest(value):
    return hashlib.sha256(value.encode() if isinstance(value, str) else value).hexdigest()


def core_fixture():
    scope = dict(project_id='project:fixture', version_id='version:v0', analysis_id='analysis:initial',
                 run_id='run:initial', source_revision='a' * 40, baseline_sha256=digest('fixture-manifest'))
    tool = dict(tool_id='fixture-analyzer', version='1.fixture', version_reason=None,
                config_sha256=digest('fixture-config'), config_reason=None)
    confidence = dict(value=0.9, reason=None)
    model = dict(provider='fixture-local-provider', model='fixture-model', revision=None,
                 revision_reason='Synthetic fixture; no serving model was run.', settings=None,
                 settings_reason='Generation settings are not available in this fixture.')

    def record(kind, identifier, **fields):
        subject = fields.pop('subject_sha256', scope['baseline_sha256'])
        return dict(schema_version='1.0.0', kind=kind, id=identifier, scope=copy.deepcopy(scope),
                    subject_sha256=subject, recorded_at='2026-11-04T00:00:00Z', **fields)

    artifacts = [dict(id='artifact:' + name, sha256=digest(name), media_type=media,
                      redaction='NO_SENSITIVE_CONTENT') for name, media in [
                          ('analysis', 'application/json'), ('tests', 'application/json'),
                          ('security', 'application/json'), ('candidate-tests', 'application/json'),
                          ('candidate-analysis', 'application/json'), ('candidate-manifest', 'application/json'),
                          ('failed-attempt', 'application/json'),
                          ('diff', 'text/x-diff'), ('context', 'text/plain')]]
    records = [
        record('SourceLocation', 'location:main', path='src/Main.java', file_id='file:main',
               file_sha256=digest(SOURCE_BYTES), resolution='RESOLVED', reason=None,
               start_line=1, start_column=2, end_line=1, end_column=5, symbol_id='symbol:main'),
        record('SourceLocation', 'location:helper', path='src/Helper.java', file_id='file:helper',
               file_sha256=digest('helper()\n'), resolution='RESOLVED', reason=None,
               start_line=1, start_column=1, end_line=1, end_column=7, symbol_id='symbol:helper'),
        record('Symbol', 'symbol:main', language='JAVA', name='Main.main', signature='void main()',
               location_id='location:main', resolution='RESOLVED', reason=None, public_api=True,
               evidence_ids=['evidence:analysis']),
        record('Symbol', 'symbol:helper', language='JAVA', name='Helper.run', signature='void run()',
               location_id='location:helper', resolution='RESOLVED', reason=None, public_api=False,
               evidence_ids=['evidence:analysis']),
        record('DependencyEdge', 'dependency:call', from_symbol_id='symbol:main', to_symbol_id='symbol:helper',
               relationship='CALL', resolution='RESOLVED', reason=None, evidence_ids=['evidence:analysis']),
    ]
    candidate_snapshot = digest('candidate-manifest')
    for name in ['analysis', 'tests', 'security', 'candidate-tests', 'candidate-analysis']:
        candidate = name in ('security', 'candidate-tests', 'candidate-analysis')
        records.append(record('Evidence', 'evidence:' + name, producer_kind='DETERMINISTIC_TOOL',
                              actor_id=None,
                              subject_sha256=candidate_snapshot if candidate else scope['baseline_sha256'],
                              tool=copy.deepcopy(tool), rule_id='fixture:' + name, model=None,
                              artifact_id='artifact:' + name, location_ids=[] if candidate else ['location:main', 'location:helper'],
                              symbol_ids=[], verification='VERIFIED', confidence=copy.deepcopy(confidence),
                              redaction='NO_SENSITIVE_CONTENT'))
    quality = record('Finding', 'finding:quality', classification='QUALITY_REFACTOR', category='COMPLEXITY',
                     rule_id='fixture:complexity', tool=copy.deepcopy(tool), location_ids=['location:main'],
                     evidence_ids=['evidence:analysis'], confidence=copy.deepcopy(confidence),
                     eligibility='ELIGIBLE', eligibility_reason=None, status='OPEN')
    security = record('Finding', 'finding:security', classification='SECURITY_REVIEW', category='SECURITY',
                      rule_id='fixture:security-review', tool=copy.deepcopy(tool), location_ids=['location:main'],
                      evidence_ids=['evidence:analysis'], confidence=copy.deepcopy(confidence),
                      eligibility='INELIGIBLE', eligibility_reason='Security review is not an ordinary quality task.',
                      status='OPEN')
    records.extend([quality, security])
    for phase, value in [('BASELINE', 10.0), ('CANDIDATE', 8.0)]:
        records.append(record('Metric', 'metric:' + phase.lower(), name='fixture-complexity', unit='COUNT', currency_code=None,
                              subject_sha256=scope['baseline_sha256'] if phase == 'BASELINE' else candidate_snapshot,
                              phase=phase, value=value, measurement='MEASURED', reason=None,
                              comparison_key=digest('fixture-tool-rule-config-scope'), direction='LOWER_IS_BETTER',
                              comparison=dict(tool=copy.deepcopy(tool), rule_set_version='fixture-rules-v1', rule_set_reason=None,
                                              measurement_scope_sha256=digest('fixture-source-scope'),
                                              environment_sha256=digest('fixture-environment'), environment_reason=None,
                                              test_suite_sha256=None, test_suite_state='NOT_APPLICABLE'),
                              population='NONE', denominator=None, attempt_ids=[],
                              evidence_ids=['evidence:analysis' if phase == 'BASELINE' else 'evidence:candidate-analysis']))
        records[-1]['comparison_key'] = metric_comparison_key(records[-1])
    records.append(record('TestResult', 'test:baseline', suite_id='suite:frozen', suite_sha256=digest('fixture-suite'),
                          tool=copy.deepcopy(tool), environment_sha256=digest('fixture-environment'),
                          execution_status='COMPLETED', outcome='PASSED', total=2, passed=2, failed=0, skipped=0,
                          reason=None, evidence_ids=['evidence:tests']))
    candidate_test = copy.deepcopy(records[-1])
    candidate_test.update(id='test:candidate', subject_sha256=candidate_snapshot,
                          evidence_ids=['evidence:candidate-tests'])
    records.append(candidate_test)
    snapshots = [dict(finding_id=quality['id'], fingerprint=finding_fingerprint(quality))]
    selection = record('IssueSelection', 'selection:first', selected_finding_ids=[quality['id']],
                       baseline_test_result_ids=['test:baseline'], snapshots=snapshots,
                       fingerprint=selection_fingerprint(scope, snapshots), actor_id='actor:fixture-user',
                       created_at='2026-11-04T00:00:00Z', approval_ref='approval:fixture-first-gate',
                       eligibility='ELIGIBLE', reasons=[])
    records.append(selection)
    included = ['finding:quality', 'symbol:main', 'symbol:helper', 'location:main', 'location:helper',
                'dependency:call', 'test:baseline']
    records.append(record('ContextPackage', 'context:bounded', selection_id='selection:first',
                          target_finding_id='finding:quality', target_symbol_id='symbol:main',
                          source_location_ids=['location:main', 'location:helper'], caller_symbol_ids=[],
                          callee_symbol_ids=['symbol:helper'], dependency_ids=['dependency:call'],
                          test_result_ids=['test:baseline'], public_api_symbol_ids=['symbol:main'],
                          known_side_effects=[], side_effect_status='KNOWN',
                          budget=dict(max_tokens=1024, used_tokens=128, measurement='MEASURED', reason=None),
                          included_ids=included, excluded=[], missing_critical_ids=[], unresolved_dependency_ids=[],
                          artifact_ids=['artifact:context'], redaction='NO_SENSITIVE_CONTENT',
                          evidence_ids=['evidence:analysis'], completeness='COMPLETE', reasons=[]))
    records.append(record('PatchCandidate', 'patch:first', job_id='job:first', attempt_id='attempt:first',
                          selection_id='selection:first', target_finding_id='finding:quality', technique='fixture:extract-method',
                          diff_artifact_id='artifact:diff', diff_sha256=digest('diff'), allowed_paths=['src/'],
                          output_snapshot_sha256=candidate_snapshot, output_manifest_artifact_id='artifact:candidate-manifest',
                          output_snapshot_reason=None,
                          changed_files=[dict(file_id='file:main', path='src/Main.java', operation='MODIFY',
                                              before_sha256=digest(SOURCE_BYTES), after_sha256=digest('fixture-candidate'))],
                          model=model, validation_ids=['validation:first'], security_finding_ids=[],
                          security_status='CLEAN', behavior_status='PASSED', quality_outcome='IMPROVED',
                          applicability='APPLICABLE', rejection_reasons=[], confidence=copy.deepcopy(confidence)))
    records.append(record('ValidationResult', 'validation:first', candidate_ids=['patch:first'], validation_scope='CANDIDATE',
                          subject_sha256=candidate_snapshot, workspace_kind='CANDIDATE_DERIVATIVE',
                          workspace_manifest_artifact_id='artifact:candidate-manifest',
                          execution_status='COMPLETED', build_status='PASSED', behavior_status='PASSED',
                          behavior_reason=None, quality_outcome='IMPROVED', quality_reason=None,
                          security_status='CLEAN', security_reason=None, security_execution_status='COMPLETED',
                          security_evidence_ids=['evidence:security'], security_finding_ids=[], test_result_ids=['test:candidate'],
                          metric_ids=['metric:baseline', 'metric:candidate'], evidence_ids=['evidence:candidate-tests'], reason=None))
    bundle = dict(schema_version='1.0.0', mode='FIXTURE', scope=scope,
                  files=[dict(id='file:main', path='src/Main.java', sha256=digest(SOURCE_BYTES),
                              subject_sha256=scope['baseline_sha256'],
                              is_symlink=False, frozen=False, protected_test=False),
                         dict(id='file:helper', path='src/Helper.java', sha256=digest('helper()\n'),
                              subject_sha256=scope['baseline_sha256'],
                              is_symlink=False, frozen=False, protected_test=False)],
                  artifacts=artifacts, test_suites=[dict(id='suite:frozen', sha256=digest('fixture-suite'),
                                                       case_ids=['case:first', 'case:second'])],
                  attempts=[dict(id='attempt:first', job_id='job:first', number=1, started=True,
                                 execution_status='COMPLETED', reason=None, failure_kind=None,
                                 evidence_ids=['evidence:candidate-tests'], artifact_ids=[]),
                            dict(id='attempt:failed', job_id='job:first', number=2, started=True,
                                 execution_status='FAILED', reason='Synthetic failed correction retained in denominators.',
                                 failure_kind='CONTRACT_REJECTION', evidence_ids=[], artifact_ids=['artifact:failed-attempt'])],
                  records=records)
    return bundle


def capability_fixture(languages=LANGUAGES):
    core = core_fixture()
    records = []
    for language in languages:
        ids = []
        for name in CAPABILITIES:
            identifier = 'capability:' + language.lower() + '-' + name
            ids.append(identifier)
            records.append(dict(schema_version='1.0.0', id=identifier, kind='Capability', scope=copy.deepcopy(core['scope']),
                                subject_sha256=core['scope']['baseline_sha256'], recorded_at='2026-11-04T00:00:00Z',
                                language=language, component_id='component:fixture', capability=name,
                                status='NOT_IMPLEMENTED', confidence=dict(value=None, reason='Interface fixture only.'),
                                tool=None, toolchain=[], evidence_ids=[], limitations=['No runtime adapter is implemented by F02.'],
                                reason='Contract declaration only; real evidence belongs to the adapter tasks.'))
        records.append(dict(schema_version='1.0.0', id='adaptercaps:' + language.lower(), kind='LanguageAdapterCapabilities',
                            subject_sha256=core['scope']['baseline_sha256'], recorded_at='2026-11-04T00:00:00Z',
                            scope=copy.deepcopy(core['scope']), adapter_id='adapter:' + language.lower(), language=language,
                            component_id='component:fixture', implementation_state='CONTRACT_DEFINED', capability_ids=ids))
    return dict(schema_version='1.0.0', mode='FIXTURE', scope=core['scope'], files=[], artifacts=[],
                test_suites=[], attempts=[], records=records)


def write_fixtures():
    directory = ROOT / 'tests/contracts/fixtures'
    directory.mkdir(parents=True, exist_ok=True)
    core = core_fixture()
    core['records'].extend(capability_fixture(('JAVA',))['records'])
    payloads = {'core.json': core, 'seven-languages.json': capability_fixture()}
    for name, payload in payloads.items():
        (directory / name).write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8', newline='\n')
    examples = ROOT / 'docs/contracts/examples'
    examples.mkdir(parents=True, exist_ok=True)
    result = dict(schema_version='1.0.0', request_id='request:fixture', status='OK', data=core, next_cursor=None)
    selection = next(r for r in core['records'] if r['kind'] == 'IssueSelection')
    error = dict(schema_version='1.0.0', request_id='request:fixture', status='ERROR', code='STALE_SELECTION',
                 component='CONTRACT', message='The selected findings have changed. A fresh selection is required.',
                 retryable=True, details=[dict(entity_id=None, field='fingerprint')])
    for name, payload in [('result.json', result), ('issue-selection.json', selection), ('error.json', error)]:
        (examples / name).write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8', newline='\n')


if __name__ == '__main__':
    write_fixtures()
