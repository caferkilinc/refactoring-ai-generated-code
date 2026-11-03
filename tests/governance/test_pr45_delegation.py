"""Revision-bound delegated approval; isolated API fixtures, no GitHub writes."""
import copy
import unittest

from test_gate import API, LIVE_PLAN
from gate import Rejected, owner_approval, readiness, verify_acceptance


SHA = 'd923134da4f9f5a2ab55a5f51fbf9415ff717262'
REPOSITORY = 'caferkilinc/refactoring-ai-generated-code'


class DelegationAPI(API):
    def __init__(self, task):
        super().__init__()
        self.current = {
            'number': 45, 'body': 'Task: #9\nPlan: F00-V0',
            'state': 'open', 'draft': False, 'merged_at': None,
            'changed_files': 1, 'user': {'login': 'caferkilinc'},
            'head': {'sha': SHA, 'ref': 'feature/9-java-v0-pilot',
                     'repo': {'full_name': REPOSITORY}},
            'base': {'ref': 'main', 'repo': {'full_name': REPOSITORY}},
        }
        self.current_comments = [{'user': {'login': 'caferkilinc'},
                                  'body': 'GENESIS-DELEGATE-APPROVED: ' + SHA}]
        self.current_checks = [
            {'name': name, 'status': 'completed', 'conclusion': 'success',
             'app': {'slug': 'github-actions'}} for name in task['required_checks']
        ]

    def call(self, path, **kwargs):
        if path == '/issues/9':
            return {'state': 'open'}
        if path == '/pulls/45':
            return self.current
        return super().call(path, **kwargs)

    def pages(self, path, key=None):
        if path == '/pulls/45/files':
            return [{'filename': 'experiments/original-ai-code/java-inventory-v0/Inventory.java'}]
        if path == '/issues/45/comments':
            return self.current_comments
        if path == '/issues/9/dependencies/blocked_by':
            return [{'number': 8}]
        if path.startswith('/commits/' + SHA + '/check-runs'):
            return self.current_checks
        return super().pages(path, key)


class DelegationTests(unittest.TestCase):
    def setUp(self):
        self.plan = copy.deepcopy(LIVE_PLAN)
        self.task = next(t for t in self.plan['tasks'] if t['plan_id'] == 'F00-V0')
        self.api = DelegationAPI(self.task)
        self.accepted = {'8': {'pr': 101, 'head_sha': 'abc',
                              'evidence': ['https://github.com/' + REPOSITORY + '/pull/101']}}

    def approve(self):
        return owner_approval(self.task, self.api.current, self.api, self.plan)

    def test_valid_delegation_passes_complete_readiness_with_real_prerequisite_policy(self):
        result = readiness(self.api.current, self.plan, self.accepted, self.api)
        self.assertIn('applicable CI verified', result)

    def test_missing_comment_fails(self):
        self.api.current_comments = []
        with self.assertRaises(Rejected):
            self.approve()

    def test_cafer_cannot_impersonate_owner_marker(self):
        self.api.current_comments[0]['body'] = 'GENESIS-OWNER-APPROVED: ' + SHA
        with self.assertRaises(Rejected):
            self.approve()

    def test_wrong_or_stale_comment_fails(self):
        for field, value in [('author', 'ismail-cevik'), ('body', 'GENESIS-DELEGATE-APPROVED: old')]:
            with self.subTest(field=field):
                original = copy.deepcopy(self.api.current_comments)
                if field == 'author':
                    self.api.current_comments[0]['user']['login'] = value
                else:
                    self.api.current_comments[0]['body'] = value
                with self.assertRaises(Rejected):
                    self.approve()
                self.api.current_comments = original

    def test_scope_cannot_expand_to_another_revision_pr_branch_repository_or_author(self):
        mutations = [
            lambda p, t, r: r.update(number=46),
            lambda p, t, r: r['head'].update(sha='0' * 40),
            lambda p, t, r: r['head'].update(ref='feature/9-other'),
            lambda p, t, r: r['head']['repo'].update(full_name='other/fork'),
            lambda p, t, r: r['head'].pop('repo'),
            lambda p, t, r: r['head'].update(repo=None),
            lambda p, t, r: r['base'].update(ref='release'),
            lambda p, t, r: r['base']['repo'].update(full_name='other/repo'),
            lambda p, t, r: r['user'].update(login='other-user'),
            lambda p, t, r: p.update(repository='other/repo'),
            lambda p, t, r: t.update(plan_id='F01-GOV'),
            lambda p, t, r: t.update(issue_number=1),
        ]
        for index, mutate in enumerate(mutations):
            with self.subTest(boundary=index):
                plan, task, pr = map(copy.deepcopy, (self.plan, self.task, self.api.current))
                mutate(plan, task, pr)
                # Supply the same purported approval even for a different PR.
                class Comments:
                    def pages(inner, path):
                        return self.api.current_comments
                with self.assertRaises(Rejected):
                    owner_approval(task, pr, Comments(), plan)

    def test_delegation_does_not_bypass_failed_missing_or_skipped_ci(self):
        for outcome in ('failure', 'skipped', 'missing'):
            with self.subTest(outcome=outcome):
                self.api.current_checks = copy.deepcopy(DelegationAPI(self.task).current_checks)
                if outcome == 'missing':
                    self.api.current_checks = []
                else:
                    self.api.current_checks[0]['conclusion'] = outcome
                with self.assertRaisesRegex(Rejected, 'Missing/failed'):
                    readiness(self.api.current, self.plan, self.accepted, self.api)

    def test_delegation_does_not_bypass_missing_prerequisite_acceptance(self):
        with self.assertRaisesRegex(Rejected, 'missing trusted acceptance record'):
            readiness(self.api.current, self.plan, {}, self.api)

    def test_historical_owner_approval_still_passes(self):
        self.api.current_comments = [{'user': {'login': 'cakarburkayy'},
                                     'body': 'GENESIS-OWNER-APPROVED: ' + SHA}]
        self.approve()

    def test_delegated_evidence_remains_verifiable_for_later_prerequisite_acceptance(self):
        self.api.current.update(merged_at='2026-11-04T00:00:00Z', state='closed')
        self.api.call = lambda path, **kwargs: (
            {'state': 'closed', 'state_reason': 'completed'} if path == '/issues/9'
            else self.api.current)
        record = {'pr': 45, 'head_sha': SHA,
                  'evidence': ['https://github.com/' + REPOSITORY + '/pull/45']}
        verify_acceptance(self.task, record, self.api, self.plan)


if __name__ == '__main__':
    unittest.main()
