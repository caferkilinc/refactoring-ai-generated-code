"""Phase 1 authority and handoff checks against a simulated read-only GitHub API."""
import copy
import unittest

from test_gate import API, LIVE_PLAN
from gate import Rejected, propose_handoff, readiness


REPO = LIVE_PLAN['repository']
HEAD = 'a' * 40
MERGED = 'b' * 40
MAIN = 'c' * 40
DEVELOPER = 'Yaman-A-E'
BRANCH = 'feature/11-contract'


class ContractAPI(API):
    def __init__(self, task):
        super().__init__()
        self.prior = API()
        self.issue = {'state': 'open'}
        self.pr = {
            'number': 102, 'body': 'Task: #11\nPlan: F02-CONTRACT',
            'user': {'login': DEVELOPER}, 'changed_files': 1,
            'state': 'open', 'draft': False,
            'base': {'ref': 'main', 'repo': {'full_name': REPO}},
            'head': {'ref': BRANCH, 'sha': HEAD, 'repo': {'full_name': REPO}},
        }
        self.files = [{'filename': 'docs/contracts/cir.md'}]
        self.comments = [{'user': {'login': DEVELOPER}, 'body':
                          f'GENESIS-DEVELOPER-APPROVED: F02-CONTRACT {REPO} {BRANCH} {HEAD} merge'}]
        self.checks = [{'name': name, 'status': 'completed', 'conclusion': 'success',
                        'app': {'slug': 'github-actions'}} for name in task['required_checks']]
        self.dependencies = [{'number': 8}]
        self.ancestry = {'status': 'ahead', 'merge_base_commit': {'sha': MERGED}}

    def call(self, path, **kwargs):
        if path in ('/issues/8', '/pulls/101'):
            return self.prior.call(path, **kwargs)
        if path == f'/compare/{MERGED}...{MAIN}':
            return self.ancestry
        return super().call(path, **kwargs)

    def pages(self, path, key=None):
        if path.startswith(('/pulls/101/', '/issues/101/', '/commits/abc/')):
            return self.prior.pages(path, key)
        return super().pages(path, key)


class CodexAuthorityTests(unittest.TestCase):
    def setUp(self):
        self.plan = copy.deepcopy(LIVE_PLAN)
        self.rotation = self.plan['sequential_execution']
        self.rotation.update(active_owner=DEVELOPER, active_task_plan_id='F02-CONTRACT',
                             rotation_index=2, next_owner_if_accepted='ismail-cevik')
        task = next(t for t in self.plan['tasks'] if t['plan_id'] == 'F02-CONTRACT')
        self.api = ContractAPI(task)
        self.accepted = {'8': {'pr': 101, 'head_sha': 'abc', 'evidence': ['https://example.org/8']}}
        self.record = {'pr': 102, 'head_sha': HEAD, 'developer': DEVELOPER,
                       'evidence': [f'https://github.com/{REPO}/pull/102']}

    def ready(self):
        return readiness(self.api.pr, self.plan, self.accepted, self.api)

    def handoff(self):
        self.api.issue = {'state': 'closed', 'state_reason': 'completed'}
        self.api.pr.update(state='closed', merged_at='2026-11-04T00:00:00Z', merge_commit_sha=MERGED)
        return propose_handoff(self.api.pr, self.plan, self.accepted, self.record, self.api, MAIN)

    def test_active_developer_needs_no_ordinary_owner_comment(self):
        self.assertIn('applicable CI verified', self.ready())

    def test_developer_marker_binds_task_repository_branch_revision_and_scope(self):
        marker = self.api.comments[0]['body']
        for field, wrong in [(1, 'F00-PLAN'), (2, 'another/repo'), (3, 'feature/11-other'),
                             (4, 'd' * 40), (5, 'push')]:
            with self.subTest(field=field):
                fields = marker.split()
                fields[field] = wrong
                self.api.comments[0]['body'] = ' '.join(fields)
                with self.assertRaisesRegex(Rejected, 'authorized developer approval'):
                    self.ready()

    def test_owner_marker_alone_cannot_approve_for_the_developer(self):
        self.api.comments = [{'user': {'login': 'cakarburkayy'},
                              'body': f'GENESIS-OWNER-APPROVED: {HEAD}'}]
        with self.assertRaisesRegex(Rejected, 'authorized developer approval'):
            self.ready()

    def test_fork_head_is_rejected(self):
        self.api.pr['head']['repo']['full_name'] = 'fork/refactoring-ai-generated-code'
        with self.assertRaisesRegex(Rejected, 'canonical repository'):
            self.ready()

    def test_protected_workflow_needs_separate_owner_comment(self):
        self.api.files = [{'filename': '.github/workflows/contract-checks.yml'}]
        with self.assertRaisesRegex(Rejected, 'Protected changes'):
            self.ready()
        self.api.comments.append({'user': {'login': 'cakarburkayy'},
                                  'body': f'GENESIS-OWNER-APPROVED: {HEAD}'})
        self.assertIn('applicable CI verified', self.ready())

    def test_rename_from_protected_path_requires_owner_approval(self):
        task = next(t for t in self.plan['tasks'] if t['plan_id'] == 'F02-CONTRACT')
        task['allowed_paths'].append('tests/fixtures/')
        self.api.files[0]['previous_filename'] = 'tests/fixtures/frozen.txt'
        with self.assertRaisesRegex(Rejected, 'Protected changes'):
            self.ready()

    def test_owner_comment_does_not_override_task_scope(self):
        self.api.files = [{'filename': 'docs/SRS.md'}]
        self.api.comments.append({'user': {'login': 'cakarburkayy'},
                                  'body': f'GENESIS-OWNER-APPROVED: {HEAD}'})
        with self.assertRaisesRegex(Rejected, 'Out-of-task path'):
            self.ready()

    def test_new_handoff_is_a_read_only_proposal(self):
        previous = copy.deepcopy((self.plan, self.accepted))
        proposal = self.handoff()
        self.assertEqual('REVIEW_REQUIRED', proposal['status'])
        self.assertEqual('ismail-cevik', proposal['proposed_owner'])
        self.assertEqual(3, proposal['proposed_index'])
        self.assertFalse(proposal['advance'])
        self.assertEqual(previous, (self.plan, self.accepted))

    def test_duplicate_after_rotation_does_not_advance_again(self):
        self.accepted['11'] = self.record
        self.rotation.update(active_owner='ismail-cevik', active_task_plan_id='F02-STATE',
                             rotation_index=3, next_owner_if_accepted='tahaugurtoyran',
                             last_accepted_handoff_key=f'F02-CONTRACT:{HEAD}')
        first = self.handoff()
        self.assertEqual(first, self.handoff())
        self.assertEqual('ALREADY_ACCEPTED', first['status'])
        self.assertFalse(first['advance'])
        self.assertEqual(3, self.rotation['rotation_index'])

    def test_conflicting_acceptance_does_not_replace_history(self):
        self.accepted['11'] = dict(self.record, head_sha='d' * 40)
        with self.assertRaisesRegex(Rejected, 'already accepted at another revision'):
            self.handoff()

    def test_new_handoff_requires_merged_revision_on_main(self):
        self.api.ancestry['status'] = 'diverged'
        with self.assertRaisesRegex(Rejected, 'not reachable'):
            self.handoff()

    def test_new_handoff_cannot_use_legacy_record_without_developer(self):
        del self.record['developer']
        with self.assertRaisesRegex(Rejected, 'active ordinary task and developer'):
            self.handoff()
