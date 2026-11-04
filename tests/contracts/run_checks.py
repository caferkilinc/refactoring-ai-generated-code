"""CI entry point: refuse missing suites/fixtures and zero-test success."""
import sys
import unittest
from pathlib import Path

DIRECTORY = Path(__file__).resolve().parent
ROOT = DIRECTORY.parents[1]
sys.path.insert(0, str(ROOT))


def verify_inventory(directory, suite):
    required = ['test_contract_models.py', 'test_contract_graph.py', 'test_api.py',
                'fixtures/core.json', 'fixtures/seven-languages.json', 'fixtures/invalid-cases.json',
                'vendor/openapi-3.1.schema.json']
    missing = [name for name in required if not (directory / name).is_file()]
    if missing:
        raise SystemExit('Required contract checks are missing: ' + ', '.join(missing))
    if not suite.countTestCases():
        raise SystemExit('No contract tests were discovered')
    def identifiers(value):
        for item in value:
            if isinstance(item, unittest.TestSuite):
                yield from identifiers(item)
            else:
                yield item.id()
    essential = {
        'test_contract_models.ModelContracts.test_all_mandatory_entities_have_valid_versioned_examples',
        'test_contract_graph.GraphContracts.test_invalid_examples_reject_the_documented_contract_failure',
        'test_contract_graph.GraphContracts.test_security_only_selection_rejected_even_with_fresh_correct_fingerprints',
        'test_contract_graph.GraphContracts.test_baseline_test_success_does_not_validate_candidate_bytes',
        'test_contract_graph.GraphContracts.test_frozen_source_and_protected_test_manifests_cannot_be_patch_targets',
        'test_api.ApiContracts.test_official_openapi_schema_is_pinned_and_the_document_validates',
    }
    if not essential <= set(identifiers(suite)):
        raise SystemExit('Required contract acceptance cases were not discovered')


def main():
    suite = unittest.defaultTestLoader.discover(str(DIRECTORY), pattern='test_*.py')
    verify_inventory(DIRECTORY, suite)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if result.skipped:
        raise SystemExit('Skipped contract tests cannot satisfy contract-checks')
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(main())
