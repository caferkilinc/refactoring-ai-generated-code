import copy
import hashlib
import json
import unittest

from support import ROOT, fixture, policy, record
from backend.core.schemas import models
from backend.core.schemas.coordinates import source_offsets
from backend.core.schemas.validation import ContractViolation, canonical_sha256, validate_bundle
from build_fixtures import SOURCE_BYTES
from pydantic import ValidationError


class ModelContracts(unittest.TestCase):
    def test_all_mandatory_entities_have_valid_versioned_examples(self):
        data = fixture()
        expected = {'Finding', 'Evidence', 'SourceLocation', 'Symbol', 'DependencyEdge', 'Metric', 'TestResult',
                    'PatchCandidate', 'ValidationResult', 'Capability', 'LanguageAdapterCapabilities',
                    'IssueSelection', 'ContextPackage'}
        self.assertEqual(expected, {r['kind'] for r in data['records']})
        for entity in data['records']:
            with self.subTest(entity=entity['id']):
                parsed = getattr(models, entity['kind']).model_validate(entity)
                self.assertEqual('1.0.0', parsed.schema_version)
        validate_bundle(data, patch_policy=policy())

    def test_unknown_model_revision_settings_and_confidence_remain_explicit(self):
        model = models.ModelProvenance.model_validate(record(fixture(), 'patch:first')['model'])
        self.assertIsNone(model.revision)
        self.assertIsNone(model.settings)
        confidence = models.Confidence(value=None, reason='No calibrated confidence was supplied.')
        self.assertIsNone(confidence.value)
        with self.assertRaises(ValidationError):
            models.Confidence(value=None, reason=None)

    def test_missing_measurement_is_not_zero(self):
        metric = copy.deepcopy(record(fixture(), 'metric:baseline'))
        metric.update(value=None, measurement='UNKNOWN', reason='Tool did not produce this measurement.')
        models.Metric.model_validate(metric)
        metric['value'] = 0
        with self.assertRaises(ValidationError):
            models.Metric.model_validate(metric)

    def test_confidence_rejects_invalid_range_type_and_nonfinite_values(self):
        for value in [-0.01, 1.01, '0.9', True, float('nan'), float('inf')]:
            with self.subTest(value=value), self.assertRaises(ValidationError):
                models.Confidence(value=value, reason=None)

    def test_llm_claim_is_not_independent_verified_evidence(self):
        evidence = copy.deepcopy(record(fixture(), 'evidence:analysis'))
        evidence.update(producer_kind='LLM', model=record(fixture(), 'patch:first')['model'])
        with self.assertRaises(ValidationError):
            models.Evidence.model_validate(evidence)
        evidence['verification'] = 'UNCONFIRMED'
        models.Evidence.model_validate(evidence)

    def test_unicode_scalar_columns_tabs_and_crlf(self):
        location = models.SourceLocation.model_validate(record(fixture(), 'location:main'))
        start, end = source_offsets(location, SOURCE_BYTES)
        self.assertEqual('α😀x', SOURCE_BYTES.decode('utf-8')[start:end])
        self.assertEqual(3, end - start)
        self.assertEqual(1, start)  # A tab is one scalar, regardless of display width.

    def test_utf16_or_byte_column_cannot_silently_exceed_scalar_range(self):
        location = copy.deepcopy(record(fixture(), 'location:main'))
        location['end_column'] = 6  # The four-scalar first line ends at exclusive column 5.
        with self.assertRaises(ContractViolation):
            source_offsets(models.SourceLocation.model_validate(location), SOURCE_BYTES)

    def test_location_requires_actual_matching_source_bytes(self):
        location = models.SourceLocation.model_validate(record(fixture(), 'location:main'))
        with self.assertRaises(ContractViolation) as caught:
            source_offsets(location, SOURCE_BYTES.replace(b'\r\n', b'\n'))
        self.assertEqual('SCOPE_MISMATCH', caught.exception.code)

    def test_unresolved_location_has_no_fabricated_coordinates(self):
        data = copy.deepcopy(record(fixture(), 'location:main'))
        data.update(resolution='UNRESOLVED', reason='Adapter cannot resolve this range.',
                    start_line=None, start_column=None, end_line=None, end_column=None)
        models.SourceLocation.model_validate(data)
        data['start_line'] = 1
        with self.assertRaises(ValidationError):
            models.SourceLocation.model_validate(data)

    def test_repository_paths_reject_traversal_absolute_encoded_and_nonportable_forms(self):
        paths = ['../x', 'src/../x', '/tmp/x', 'C:/x', 'C:\\x', '\\\\server\\x', 'src//x',
                 'src/%2e%2e/x', '.git/config', 'src/CON.java', 'src/name.', 'src/e\u0301.java', 'src/\x00x', 'src/\ud800.java']
        for path in paths:
            data = copy.deepcopy(record(fixture(), 'location:main'))
            data['path'] = path
            with self.subTest(path=repr(path)), self.assertRaises(ValidationError):
                models.SourceLocation.model_validate(data)

    def test_json_canonicalization_is_standard_and_key_order_independent(self):
        expected_bytes = '{"a":1,"b":"€"}'.encode('utf-8')
        expected = hashlib.sha256(expected_bytes).hexdigest()
        self.assertEqual(expected, canonical_sha256({'b': '€', 'a': 1.0}))
        self.assertEqual(expected, canonical_sha256({'a': 1, 'b': '€'}))

    def test_utc_actor_and_unknown_versions_are_strict(self):
        selection = copy.deepcopy(record(fixture(), 'selection:first'))
        for field, value in [('created_at', '2026-11-04T00:00:00+03:00'),
                             ('created_at', '2026-02-30T00:00:00Z'), ('schema_version', '1.1.0')]:
            bad = dict(selection, **{field: value})
            with self.subTest(field=field, value=value), self.assertRaises(ValidationError):
                models.IssueSelection.model_validate(bad)

    def test_invalid_utf8_and_standalone_cr_are_not_silently_translated(self):
        for source in [b'x\r', b'\xff']:
            data = copy.deepcopy(record(fixture(), 'location:main'))
            data.update(start_column=1, end_column=2, file_sha256=hashlib.sha256(source).hexdigest())
            with self.subTest(source=source), self.assertRaises(ContractViolation):
                source_offsets(models.SourceLocation.model_validate(data), source)

    def test_provider_settings_reject_credential_fields(self):
        data = copy.deepcopy(record(fixture(), 'patch:first')['model'])
        data.update(settings={'api_key': 'not-a-real-key'}, settings_reason=None)
        with self.assertRaises(ValidationError):
            models.ModelProvenance.model_validate(data)

    def test_metric_units_do_not_invent_fractional_counts_or_currency(self):
        data = copy.deepcopy(record(fixture(), 'metric:baseline'))
        data['value'] = 1.5
        with self.assertRaises(ValidationError):
            models.Metric.model_validate(data)
        data.update(unit='CURRENCY', value=1.5)
        with self.assertRaises(ValidationError):
            models.Metric.model_validate(data)
        data['currency_code'] = 'USD'
        models.Metric.model_validate(data)


if __name__ == '__main__':
    unittest.main()
