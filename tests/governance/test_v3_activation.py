"""Exact activation, regular-task isolation and immutable product-state tests."""
import copy
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts/governance'))

import gate
from v3_activation import BRANCH, OWNER, REPO, verify


class API:
    def __init__(self, test):
        self.t = test

    def call(self, path):
        if path.startswith('/git/commits/'):
            return {'parents': [{'sha': self.t.grant['source_main']}]}
        if path == '/issues/1':
            return {'state': 'open'}
        raise AssertionError(path)

    def pages(self, path, key=None):
        if path.endswith('/files'):
            return self.t.files
        if path.endswith('/blocked_by'):
            return self.t.native
        if path.endswith('/comments'):
            return self.t.comments
        if '/check-runs?' in path:
            return self.t.runs
        raise AssertionError(path)


class ActivationTests(unittest.TestCase):
    def setUp(self):
        self.plan = json.loads((ROOT / '.github/task-plan.json').read_bytes())
        self.accepted = json.loads((ROOT / '.github/acceptance.json').read_bytes())['accepted']
        self.grant = dict(pr=100, author=OWNER, head='a' * 40, source_main='b' * 40,
                          paths=['.agents/skills/next-step/SKILL.md', 'AGENTS.md'])
        repo = {'full_name': REPO}
        self.pr = dict(number=100, body='Task: #1\nPlan: F01-GOV', state='open', changed_files=2,
                       user={'login': OWNER}, base={'repo': repo.copy(), 'ref': 'main', 'sha': 'c' * 40},
                       head={'repo': repo.copy(), 'ref': BRANCH, 'sha': self.grant['head']})
        self.files = [{'filename': path} for path in self.grant['paths']]
        self.native = []
        self.comments = [{'user': {'login': OWNER}, 'body': 'GENESIS-OWNER-APPROVED: ' + self.grant['head']}]
        self.runs = [dict(name=name, head_sha=self.grant['head'], status='completed', conclusion='success',
                          app={'id': 15368, 'slug': 'github-actions'})
                     for name in ('governance-tests', 'documentation-checks', 'security-checks', 'pilot-checks')]

    def verify(self, readiness=True):
        return verify(self.pr, self.plan, self.accepted, API(self), self.grant, readiness)

    def test_exact_migration_keeps_plan_and_acceptance(self):
        before = copy.deepcopy((self.plan, self.accepted))
        self.assertIn('product rotation unaffected', self.verify())
        self.assertEqual(before, (self.plan, self.accepted))
        self.assertEqual({'8', '9'}, set(self.accepted))

    def test_wrong_branch_repository_actor_task_head_and_pr_fail_closed(self):
        for path, value in [(('head', 'ref'), 'chore/1-wrong'), (('head', 'repo'), {'full_name': 'fork/example'}),
                            (('user', 'login'), 'untrusted'), (('body',), 'Task: #11\nPlan: F02-CONTRACT'),
                            (('head', 'sha'), 'd' * 40), (('number',), 200)]:
            with self.subTest(path=path):
                original = copy.deepcopy(self.pr)
                current = self.pr[path[0]] if len(path) == 2 else self.pr
                current[path[-1]] = value
                with self.assertRaises(gate.Rejected):
                    self.verify()
                self.pr = original

    def test_scope_and_native_dependency_changes_fail_closed(self):
        self.files[0]['filename'] = '.github/acceptance.json'
        with self.assertRaisesRegex(gate.Rejected, 'exact reviewed manifest'):
            self.verify()
        self.files[0]['filename'] = self.grant['paths'][0]
        self.native.append({'number': 9})
        with self.assertRaisesRegex(gate.Rejected, 'Native migration dependencies'):
            self.verify()

    def test_exact_authenticated_owner_required(self):
        self.comments[0]['user']['login'] = 'untrusted'
        with self.assertRaisesRegex(gate.Rejected, 'project owner authorization'):
            self.verify(False)

    def test_missing_failed_and_stale_ci_block_readiness(self):
        for state in ('missing', 'failure', 'stale'):
            with self.subTest(state=state):
                prior = copy.deepcopy(self.runs)
                if state == 'missing':
                    self.runs.pop()
                elif state == 'failure':
                    self.runs[-1]['conclusion'] = 'failure'
                else:
                    self.runs[-1]['head_sha'] = 'e' * 40
                with self.assertRaisesRegex(gate.Rejected, 'pilot-checks'):
                    self.verify()
                self.runs = prior

    def test_ordinary_gate_still_requires_active_product_actor(self):
        self.pr.update(body='Task: #11\nPlan: F02-CONTRACT')
        self.pr['head']['ref'] = 'feature/11-contract'
        with patch.object(API, 'call', return_value={'state': 'open'}):
            with self.assertRaisesRegex(gate.Rejected, 'not the authorized active developer'):
                gate.evaluate(self.pr, self.plan, self.accepted, API(self))


if __name__ == '__main__':
    unittest.main()
