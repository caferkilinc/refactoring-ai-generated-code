import copy
import json
import unittest

from support import ROOT, fixture, mutate_recipe, policy, record
from backend.core.schemas.adapter import require_capability
from backend.core.schemas.models import AdapterRequest, ContractBundle, LANGUAGES
from backend.core.schemas.validation import (ContractViolation, finding_fingerprint,
                                             selection_fingerprint, metric_comparison_key, validate_bundle)


class GraphContracts(unittest.TestCase):
    def assert_rejected(self, data, code, trusted_policy=None):
        with self.assertRaises(ContractViolation) as caught:
            validate_bundle(data, patch_policy=policy() if trusted_policy is None else trusted_policy)
        self.assertEqual(code, caught.exception.code)

    def test_invalid_examples_reject_the_documented_contract_failure(self):
        recipes = json.loads((ROOT / 'tests/contracts/fixtures/invalid-cases.json').read_text())
        self.assertGreaterEqual(len(recipes), 18)
        for recipe in recipes:
            with self.subTest(case=recipe['case']):
                self.assert_rejected(mutate_recipe(fixture(), recipe), recipe['code'])

    def test_security_only_selection_rejected_even_with_fresh_correct_fingerprints(self):
        data = fixture()
        selected = record(data, 'selection:first')
        security = record(data, 'finding:security')
        selected['selected_finding_ids'] = [security['id']]
        selected['snapshots'] = [dict(finding_id=security['id'], fingerprint=finding_fingerprint(security))]
        selected['fingerprint'] = selection_fingerprint(data['scope'], selected['snapshots'])
        self.assert_rejected(data, 'VALIDATION_FAILED')

    def test_selection_detects_changed_evidence_and_confidence(self):
        for field, value in [('rule_id', 'fixture:changed-rule'), ('confidence', dict(value=0.2, reason=None))]:
            data = fixture()
            record(data, 'finding:quality')[field] = value
            with self.subTest(field=field):
                self.assert_rejected(data, 'STALE_SELECTION')

    def test_duplicate_entity_identity_is_rejected(self):
        data = fixture()
        data['records'].append(copy.deepcopy(data['records'][0]))
        self.assert_rejected(data, 'BROKEN_REFERENCE')

    def test_frozen_source_and_protected_test_manifests_cannot_be_patch_targets(self):
        for flag in ['frozen', 'protected_test', 'is_symlink']:
            baseline = fixture()
            baseline['files'][0][flag] = True
            with self.subTest(flag=flag):
                self.assert_rejected(baseline, 'FORBIDDEN_SCOPE', policy(baseline))

    def test_candidate_cannot_redefine_trusted_file_flags(self):
        trusted = fixture()
        trusted['files'][0]['protected_test'] = True
        request = fixture()  # The request attempts to remove that protected flag.
        self.assert_rejected(request, 'SCOPE_MISMATCH', policy(trusted))

    def test_trusted_policy_overrides_candidate_allowlist(self):
        data = fixture()
        record(data, 'patch:first')['allowed_paths'] = ['src/']
        self.assert_rejected(data, 'FORBIDDEN_SCOPE', policy(protected_paths=('src/Main.java',)))

    def test_patch_cannot_supply_its_own_trusted_policy(self):
        with self.assertRaises(ContractViolation) as caught:
            validate_bundle(fixture())
        self.assertEqual('FORBIDDEN_SCOPE', caught.exception.code)

    def test_stale_baseline_rejected_against_the_actual_trusted_snapshot(self):
        data = fixture()
        data['scope']['version_id'] = 'version:stale'
        for item in data['records']:
            item['scope']['version_id'] = 'version:stale'
        selected = record(data, 'selection:first')
        selected['snapshots'][0]['fingerprint'] = finding_fingerprint(record(data, 'finding:quality'))
        selected['fingerprint'] = selection_fingerprint(data['scope'], selected['snapshots'])
        self.assert_rejected(data, 'SCOPE_MISMATCH')

    def test_baseline_test_success_does_not_validate_candidate_bytes(self):
        data = fixture()
        record(data, 'validation:first')['test_result_ids'] = ['test:baseline']
        self.assert_rejected(data, 'SCOPE_MISMATCH')

    def test_baseline_security_success_does_not_validate_candidate_bytes(self):
        data = fixture()
        record(data, 'validation:first')['security_evidence_ids'] = ['evidence:analysis']
        self.assert_rejected(data, 'SCOPE_MISMATCH')

    def test_invalid_validation_back_reference_is_rejected(self):
        data = fixture()
        record(data, 'validation:first')['candidate_ids'] = ['patch:other']
        self.assert_rejected(data, 'BROKEN_REFERENCE')

    def test_missing_scan_cannot_propagate_clean_to_patch(self):
        data = fixture()
        validation = record(data, 'validation:first')
        validation.update(security_status='UNAVAILABLE', security_execution_status='UNAVAILABLE',
                          security_reason='Scanner tool is unavailable.', security_evidence_ids=[])
        self.assert_rejected(data, 'VALIDATION_FAILED')

    def test_successful_build_alone_is_not_behavioral_pass(self):
        data = fixture()
        record(data, 'validation:first')['test_result_ids'] = []
        self.assert_rejected(data, 'INVALID_CONTRACT')

    def test_zero_test_suite_is_not_pass(self):
        data = fixture()
        record(data, 'test:candidate').update(total=0, passed=0, failed=0, skipped=0)
        self.assert_rejected(data, 'INVALID_CONTRACT')

    def test_quality_requires_measured_comparable_inputs(self):
        data = fixture()
        record(data, 'metric:candidate')['comparison_key'] = '0' * 64
        self.assert_rejected(data, 'VALIDATION_FAILED')

    def test_behavior_and_quality_are_independent_for_all_required_combinations(self):
        for outcome, value in [('IMPROVED', 8.0), ('UNCHANGED', 10.0), ('WORSE', 12.0)]:
            data = fixture()
            record(data, 'metric:candidate')['value'] = value
            record(data, 'validation:first')['quality_outcome'] = outcome
            record(data, 'patch:first')['quality_outcome'] = outcome
            with self.subTest(behavior='PASSED', quality=outcome):
                parsed = validate_bundle(data, patch_policy=policy())
                validation = next(r for r in parsed.records if r.kind == 'ValidationResult')
                self.assertEqual(('PASSED', outcome), (validation.behavior_status, validation.quality_outcome))
        data = fixture()
        record(data, 'validation:first').update(execution_status='INCOMPLETE', build_status='UNVERIFIED',
            behavior_status='UNVERIFIED', behavior_reason='Candidate tests did not run.', quality_outcome='NOT_COMPARABLE',
            quality_reason='Measurements are unavailable.', security_status='UNAVAILABLE', security_reason='Scanner unavailable.',
            security_execution_status='UNAVAILABLE', security_evidence_ids=[], test_result_ids=[], metric_ids=[],
            reason='Toolchain is unavailable.')
        record(data, 'patch:first').update(applicability='UNVERIFIED', rejection_reasons=['Validation is incomplete.'],
            behavior_status='UNVERIFIED', quality_outcome='NOT_COMPARABLE', security_status='UNAVAILABLE')
        validate_bundle(data, patch_policy=policy())

    def test_failed_attempts_remain_in_started_and_planned_denominators(self):
        data = fixture()
        metric = copy.deepcopy(record(data, 'metric:baseline'))
        metric.update(id='metric:success-rate', unit='PERCENT', value=50.0, population='STARTED_ATTEMPTS',
                      denominator=2, attempt_ids=['attempt:first', 'attempt:failed'])
        metric['comparison_key'] = metric_comparison_key(metric)
        data['records'].append(metric)
        validate_bundle(data, patch_policy=policy())
        metric.update(denominator=1, attempt_ids=['attempt:first'])
        self.assert_rejected(data, 'VALIDATION_FAILED')

    def test_complete_context_cannot_hide_an_unresolved_dependency(self):
        data = fixture()
        edge = record(data, 'dependency:call')
        edge.update(resolution='UNRESOLVED', reason='Dynamic dispatch target could not be resolved.')
        self.assert_rejected(data, 'INCOMPLETE_CONTEXT')

    def test_complete_context_cannot_drop_critical_included_references(self):
        data = fixture()
        record(data, 'context:bounded')['included_ids'].remove('symbol:helper')
        self.assert_rejected(data, 'INCOMPLETE_CONTEXT')

    def test_context_secret_masking_state_is_not_silently_complete(self):
        data = fixture()
        context_artifact = next(a for a in data['artifacts'] if a['id'] == 'artifact:context')
        context_artifact['redaction'] = 'UNREVIEWED'
        self.assert_rejected(data, 'INCOMPLETE_CONTEXT')

    def test_all_seven_languages_have_independent_nonimplemented_capabilities(self):
        bundle = validate_bundle(fixture('seven-languages.json'))
        adapters = [r for r in bundle.records if r.kind == 'LanguageAdapterCapabilities']
        self.assertEqual(set(LANGUAGES), {r.language for r in adapters})
        self.assertTrue(all(r.implementation_state == 'CONTRACT_DEFINED' for r in adapters))
        self.assertTrue(all(r.status == 'NOT_IMPLEMENTED' for r in bundle.records if r.kind == 'Capability'))

    def test_capability_request_rejects_unavailable_and_wrong_operation(self):
        data = fixture()
        request = AdapterRequest(schema_version='1.0.0', scope=data['scope'], language='JAVA',
            component_id='component:fixture', adapter_capabilities_id='adaptercaps:java',
            capability_id='capability:java-parse', operation='parse', input_artifact_id='artifact:analysis', timeout_seconds=30)
        with self.assertRaises(ContractViolation) as caught:
            require_capability(request, ContractBundle.model_validate(data), patch_policy=policy())
        self.assertEqual('UNAVAILABLE_CAPABILITY', caught.exception.code)
        cap = record(data, 'capability:java-parse')
        cap.update(status='SUPPORTED', tool=record(data, 'evidence:analysis')['tool'], evidence_ids=['evidence:analysis'],
                   toolchain=[dict(name='fixture-parser', version='1.fixture', status='AVAILABLE', reason=None)])
        record(data, 'adaptercaps:java')['implementation_state'] = 'RUNTIME_IMPLEMENTED'
        # Hypothetical production-format metadata for a pure guard test, not execution evidence.
        data['mode'] = 'INTERCHANGE'
        parsed = validate_bundle(data, patch_policy=policy())
        self.assertEqual('parse', require_capability(request, parsed, patch_policy=policy()).capability)
        request.operation = 'test'
        with self.assertRaises(ContractViolation):
            require_capability(request, parsed, patch_policy=policy())

    def test_error_envelope_never_echoes_invalid_source_or_local_path(self):
        data = fixture()
        raw_secret_path = 'C:/local/private/never-echo.java'
        record(data, 'location:main')['path'] = raw_secret_path
        try:
            validate_bundle(data, patch_policy=policy())
        except ContractViolation as error:
            encoded = json.dumps(error.envelope())
            self.assertNotIn(raw_secret_path, encoded)
            self.assertNotIn('Traceback', encoded)
            self.assertEqual('INVALID_CONTRACT', error.code)
        else:
            self.fail('Invalid local path unexpectedly passed')

    def test_frozen_suite_cannot_be_replaced_with_a_smaller_passing_suite(self):
        data = fixture()
        data['test_suites'][0]['case_ids'] = ['case:first']
        record(data, 'test:baseline').update(total=1, passed=1)
        record(data, 'test:candidate').update(total=1, passed=1)
        self.assert_rejected(data, 'SCOPE_MISMATCH')

    def test_new_file_is_bound_to_candidate_snapshot_and_trusted_path_scope(self):
        data = fixture()
        patch = record(data, 'patch:first')
        data['files'].append(dict(id='file:new', path='src/New.java', sha256='1' * 64,
            subject_sha256=patch['output_snapshot_sha256'], is_symlink=False, frozen=False, protected_test=False))
        patch['changed_files'].append(dict(file_id='file:new', path='src/New.java', operation='ADD',
                                           before_sha256=None, after_sha256='1' * 64))
        validate_bundle(data, patch_policy=policy())
        patch['changed_files'][-1]['after_sha256'] = '2' * 64
        self.assert_rejected(data, 'FORBIDDEN_SCOPE')

    def test_combined_validation_is_a_separate_fresh_workspace_result(self):
        data = fixture()
        combined = copy.deepcopy(record(data, 'validation:first'))
        combined.update(id='validation:combined', validation_scope='COMBINED', workspace_kind='FRESH_V0_COMBINATION')
        data['records'].append(combined)
        record(data, 'patch:first')['validation_ids'].append('validation:combined')
        validate_bundle(data, patch_policy=policy())
        combined['workspace_kind'] = 'CANDIDATE_DERIVATIVE'
        self.assert_rejected(data, 'INVALID_CONTRACT')

    def test_declared_support_rejects_a_missing_toolchain_even_with_parser_evidence(self):
        data = fixture()
        cap = record(data, 'capability:java-parse')
        cap.update(status='SUPPORTED', tool=record(data, 'evidence:analysis')['tool'], evidence_ids=['evidence:analysis'],
            toolchain=[dict(name='fixture-parser', version='1.fixture', status='UNAVAILABLE', reason='Not installed.')])
        self.assert_rejected(data, 'INVALID_CONTRACT')

    def test_failed_attempt_retains_its_rejection_receipt(self):
        data = fixture()
        data['attempts'][1]['artifact_ids'] = []
        self.assert_rejected(data, 'VALIDATION_FAILED')

    def test_claimed_comparison_key_cannot_hide_a_different_tool_configuration(self):
        data = fixture()
        metric = record(data, 'metric:candidate')
        metric['comparison']['tool']['version'] = 'different-version'
        self.assert_rejected(data, 'VALIDATION_FAILED')

    def test_llm_annotation_can_be_retained_alongside_independent_evidence(self):
        data = fixture()
        evidence = copy.deepcopy(record(data, 'evidence:analysis'))
        evidence.update(id='evidence:llm', producer_kind='LLM', verification='UNCONFIRMED',
                        model=record(data, 'patch:first')['model'])
        data['records'].append(evidence)
        finding = record(data, 'finding:quality')
        finding['evidence_ids'].append('evidence:llm')
        selected = record(data, 'selection:first')
        selected['snapshots'][0]['fingerprint'] = finding_fingerprint(finding)
        selected['fingerprint'] = selection_fingerprint(data['scope'], selected['snapshots'])
        validate_bundle(data, patch_policy=policy())

    def test_finding_range_can_resolve_to_its_containing_target_symbol(self):
        data = fixture()
        inside = copy.deepcopy(record(data, 'location:main'))
        inside.update(id='location:inside', start_column=3, end_column=4)
        data['records'].append(inside)
        record(data, 'evidence:analysis')['location_ids'].append('location:inside')
        finding = record(data, 'finding:quality')
        finding['location_ids'] = ['location:inside']
        selected = record(data, 'selection:first')
        selected['snapshots'][0]['fingerprint'] = finding_fingerprint(finding)
        selected['fingerprint'] = selection_fingerprint(data['scope'], selected['snapshots'])
        context = record(data, 'context:bounded')
        context['source_location_ids'].append('location:inside')
        context['included_ids'].append('location:inside')
        validate_bundle(data, patch_policy=policy())


if __name__ == '__main__':
    unittest.main()
