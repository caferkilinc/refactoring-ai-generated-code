"""Transfer identity and legacy grant boundaries; no actual hosted transfer."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import test_task_execution as execution
from gate import Rejected, owner_approval
from repository_identity import (ALIASES, DESTINATION, ORIGINAL, REPOSITORY_ID,
                                 current_repository, effective_plan, repository_urls)


class DestinationAPI:
    def __init__(self, info=None):
        self.info = info if info is not None else dict(full_name=DESTINATION, id=REPOSITORY_ID)
        self.comments = []

    def call(self, path):
        if path != '/':
            raise AssertionError(path)
        return self.info

    def pages(self, path):
        if path not in ('/issues/45/comments', '/issues/46/comments'):
            raise AssertionError(path)
        return self.comments


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
        plan = json.loads((execution.ROOT / '.github/task-plan.json').read_bytes())
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

    def test_historical_pr45_grant_survives_only_for_the_exact_original_revision(self):
        head = 'd923134da4f9f5a2ab55a5f51fbf9415ff717262'
        task = dict(plan_id='F00-V0', issue_number=9)
        plan = dict(repository=DESTINATION)
        pr = dict(number=45, user={'login': 'caferkilinc'},
                  head={'sha': head, 'ref': 'feature/9-java-v0-pilot', 'repo': {'full_name': DESTINATION}},
                  base={'ref': 'main', 'repo': {'full_name': DESTINATION}})
        api = DestinationAPI()
        api.comments = [dict(user={'login': 'caferkilinc'}, body='GENESIS-DELEGATE-APPROVED: ' + head)]
        owner_approval(task, pr, api, plan)
        for altered in [dict(pr, head=dict(pr['head'], sha='a' * 40)),
                        dict(pr, user={'login': 'Yaman-A-E'}), dict(pr, number=46),
                        dict(pr, head=dict(pr['head'], ref='feature/9-other'))]:
            with self.subTest(pr=altered), self.assertRaises(Rejected):
                owner_approval(task, altered, api, plan)
        api.info['id'] = 1
        with self.assertRaisesRegex(ValueError, 'immutable repository ID'):
            owner_approval(task, pr, api, plan)

    def test_new_process_uses_destination_for_task_lifecycle_and_publisher(self):
        with tempfile.TemporaryDirectory(prefix='genesis-transfer-') as name:
            directory = Path(name)
            subprocess.run(['git', 'init', '-q', str(directory)], check=True)
            subprocess.run(['git', '-C', str(directory), 'remote', 'add', 'origin',
                            f'https://github.com/{DESTINATION}.git'], check=True)
            env = dict(os.environ, GITHUB_REPOSITORY=DESTINATION, PYTHONDONTWRITEBYTECODE='1',
                       PYTHONPATH=os.pathsep.join((str(execution.ROOT / 'scripts/governance'),
                                                 str(execution.ROOT / 'tests/governance'))))
            script = ('import task_execution,lifecycle,safe_publish; '
                      f'assert task_execution.REPO == lifecycle.REPO == safe_publish.REPO == {DESTINATION!r}; '
                      f'assert "https://github.com/{DESTINATION}.git" in task_execution.URLS; '
                      f'assert "https://github.com/{ORIGINAL}.git" not in task_execution.URLS; '
                      'import test_task_execution as fixture; '
                      'case=fixture.ExecutionTests(); case.setUp(); '
                      'assert case.start()["status"] == "TASK_AUTHORIZED"; '
                      'from test_safe_publish import FakeGitHub; '
                      'api=FakeGitHub(case, [fixture.FILE]); '
                      f'assert api.call("/")["id"] == {REPOSITORY_ID}; '
                      'case.doCleanups()')
            result = subprocess.run([sys.executable, '-B', '-c', script], cwd=directory, env=env,
                                    text=True, capture_output=True)
            self.assertEqual(0, result.returncode, result.stderr)


if __name__ == '__main__':
    unittest.main()
