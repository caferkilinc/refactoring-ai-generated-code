"""Transfer identity and canonical repository boundaries; no actual hosted transfer."""
import copy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts/governance'))
from repository_identity import (ALIASES, DESTINATION, ORIGINAL, REPOSITORY_ID,
                                 current_repository, effective_plan, repository_urls)


class DestinationAPI:
    def __init__(self, info=None):
        self.info = info if info is not None else dict(full_name=DESTINATION, id=REPOSITORY_ID)

    def call(self, path):
        if path != '/':
            raise AssertionError(path)
        return self.info


class RepositoryTransferTests(unittest.TestCase):
    def test_exact_origins_and_workflow_identity_must_agree(self):
        for repository in ALIASES:
            for origin in repository_urls(repository):
                self.assertEqual(repository, current_repository({}, origin))
                self.assertEqual(repository, current_repository({'GITHUB_REPOSITORY': repository}, origin))
        for declared, origin in [(DESTINATION, f'https://github.com/{ORIGINAL}.git'),
                                 (ORIGINAL, f'https://github.com/{DESTINATION}.git'),
                                 ('attacker/fork', '')]:
            with self.subTest(declared=declared, origin=origin), self.assertRaises(ValueError):
                current_repository({'GITHUB_REPOSITORY': declared}, origin)
        with self.assertRaises(ValueError):
            repository_urls('attacker/fork')

    def test_destination_requires_original_numeric_id_and_preserves_registry_bytes(self):
        plan = json.loads((Path(__file__).resolve().parents[2] / '.github/task-plan.json').read_bytes())
        before = copy.deepcopy(plan)
        for info in [dict(full_name=DESTINATION, id=1), dict(full_name=ORIGINAL, id=REPOSITORY_ID),
                     dict(full_name=DESTINATION, id=str(REPOSITORY_ID)), {}]:
            with self.subTest(info=info), self.assertRaises(ValueError):
                effective_plan(plan, DestinationAPI(info), DESTINATION)
        runtime = effective_plan(plan, DestinationAPI(), DESTINATION)
        self.assertEqual(DESTINATION, runtime['repository'])
        self.assertEqual(plan['sequential_execution'], runtime['sequential_execution'])
        self.assertEqual(plan['tasks'], runtime['tasks'])
        self.assertEqual(before, plan)
        self.assertIs(plan, effective_plan(plan, None, ORIGINAL))
        with self.assertRaises(ValueError):
            effective_plan(runtime, None, ORIGINAL)

if __name__ == '__main__':
    unittest.main()
