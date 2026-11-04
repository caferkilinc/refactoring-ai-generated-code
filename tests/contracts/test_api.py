import copy
import hashlib
import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from support import ROOT, fixture, policy, record
from backend.core.schemas.export import generated_files
from backend.core.schemas.models import ErrorEnvelope, ResultEnvelope
from backend.core.schemas.validation import validate_bundle


class ApiContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads((ROOT / 'backend/core/schemas/cir-1.0.0.schema.json').read_text(encoding='utf-8'))
        cls.api = json.loads((ROOT / 'docs/contracts/openapi-1.0.0.json').read_text(encoding='utf-8'))
        cls.official = json.loads((ROOT / 'tests/contracts/vendor/openapi-3.1.schema.json').read_text(encoding='utf-8'))

    def test_official_openapi_schema_is_pinned_and_the_document_validates(self):
        raw = (ROOT / 'tests/contracts/vendor/openapi-3.1.schema.json').read_bytes()
        self.assertEqual('66f9c674bff99e11d584e7c0162ac159218b9595f418fea9e443b2d78174d44c',
                         hashlib.sha256(raw).hexdigest())
        Draft202012Validator.check_schema(self.official)
        Draft202012Validator(self.official).validate(self.api)
        invalid = copy.deepcopy(self.api)
        del invalid['info']
        with self.assertRaises(ValidationError):
            Draft202012Validator(self.official).validate(invalid)

    def test_exported_json_schema_is_valid_and_independently_checks_both_bundles(self):
        Draft202012Validator.check_schema(self.schema)
        validator = Draft202012Validator(self.schema)
        validator.validate(fixture())
        validator.validate(fixture('seven-languages.json'))

    def test_independent_schema_rejects_missing_wrong_type_enum_and_version(self):
        for field, value in [('schema_version', '9.0.0'), ('mode', True), ('mode', 'RUNTIME_IMPLEMENTED')]:
            data = fixture()
            data[field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValidationError):
                Draft202012Validator(self.schema).validate(data)
        data = fixture()
        del record(data, 'finding:quality')['rule_id']
        with self.assertRaises(ValidationError):
            Draft202012Validator(self.schema).validate(data)

    def test_generated_exports_are_byte_deterministic_and_current(self):
        for path, expected in generated_files().items():
            with self.subTest(path=str(path.relative_to(ROOT))):
                self.assertEqual(expected.encode('utf-8'), path.read_bytes())

    def test_all_external_examples_exist_and_match_actual_components(self):
        count = 0
        for path_item in self.api['paths'].values():
            for operation in path_item.values():
                self.assertEqual('CONTRACT_DEFINED', operation['x-implementation-status'])
                contents = [r.get('content', {}) for r in operation['responses'].values()]
                if 'requestBody' in operation:
                    contents.append(operation['requestBody']['content'])
                for content in contents:
                    for media in content.values():
                        for example in media.get('examples', {}).values():
                            name = example['externalValue']
                            self.assertTrue(name.startswith('examples/') and '..' not in name)
                            value = json.loads((ROOT / 'docs/contracts' / name).read_text(encoding='utf-8'))
                            schema = dict(media['schema'], components=self.api['components'])
                            Draft202012Validator(schema).validate(value)
                            count += 1
        self.assertGreater(count, 0)

    def test_result_example_has_real_reference_validation_not_only_json_parsing(self):
        value = json.loads((ROOT / 'docs/contracts/examples/result.json').read_text(encoding='utf-8'))
        result = ResultEnvelope.model_validate(value)
        self.assertEqual('FIXTURE', result.data.mode)
        validate_bundle(result.data, patch_policy=policy())
        selection = json.loads((ROOT / 'docs/contracts/examples/issue-selection.json').read_text(encoding='utf-8'))
        self.assertEqual(record(value['data'], 'selection:first'), selection)

    def test_error_example_preserves_stable_origin_retryability_and_safe_message(self):
        value = json.loads((ROOT / 'docs/contracts/examples/error.json').read_text(encoding='utf-8'))
        error = ErrorEnvelope.model_validate(value)
        self.assertEqual(('STALE_SELECTION', 'CONTRACT', True), (error.code, error.component, error.retryable))
        self.assertNotIn('Traceback', error.message)

    def test_ci_entry_point_rejects_zero_tests_and_missing_required_cases(self):
        from run_checks import DIRECTORY, verify_inventory
        with self.assertRaisesRegex(SystemExit, 'No contract tests'):
            verify_inventory(DIRECTORY, unittest.TestSuite())
        dummy = unittest.TestSuite([unittest.FunctionTestCase(lambda: None)])
        with self.assertRaisesRegex(SystemExit, 'Required contract acceptance'):
            verify_inventory(DIRECTORY, dummy)


if __name__ == '__main__':
    unittest.main()
