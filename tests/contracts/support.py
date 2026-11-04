"""Read immutable fixture inputs; apply small invalid-example recipes in memory."""
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from backend.core.schemas.models import FileIdentity, Scope, TestSuite
from backend.core.schemas.validation import PatchPolicy


def fixture(name='core.json'):
    return json.loads((ROOT / 'tests/contracts/fixtures' / name).read_text(encoding='utf-8'))


def record(bundle, identifier):
    return next(item for item in bundle['records'] if item['id'] == identifier)


def policy(bundle=None, *, protected_paths=None):
    # This trusted snapshot is intentionally separate from the mutated request.
    baseline = fixture() if bundle is None else bundle
    values = dict(expected_scope=Scope.model_validate(baseline['scope']), allowed_paths=('src/',),
                  expected_files=tuple(FileIdentity.model_validate(file) for file in baseline['files']
                                       if file['subject_sha256'] == baseline['scope']['baseline_sha256']),
                  expected_test_suites=tuple(TestSuite.model_validate(suite) for suite in baseline['test_suites']))
    if protected_paths is not None:
        values['protected_paths'] = protected_paths
    return PatchPolicy(**values)


def mutate_recipe(baseline, recipe):
    value = copy.deepcopy(baseline)
    for change in recipe['changes']:
        target = value if change['target'] == '$bundle' else record(value, change['target'])
        pieces = change['field'].split('.')
        for piece in pieces[:-1]:
            target = target[int(piece)] if isinstance(target, list) else target[piece]
        key = int(pieces[-1]) if isinstance(target, list) else pieces[-1]
        if change.get('remove'):
            del target[key]
        else:
            target[key] = copy.deepcopy(change['value'])
    return value
