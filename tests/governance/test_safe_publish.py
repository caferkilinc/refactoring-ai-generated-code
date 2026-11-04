"""Publication transactions in disposable Git repositories with a fake GitHub."""
import base64
import copy
import json
import unittest
from unittest.mock import patch

import test_task_execution as execution
from gate import Rejected
from safe_publish import (GITHUB_ACTIONS_APP, HOSTED, REPO, active_protection, publish,
                          push_commit, trusted_activation)


class FakeGitHub:
    def __init__(self, fixture, files):
        self.fixture = fixture
        self.base = fixture.repo.fixture_main
        self.main = self.base
        self.branch = fixture.contract['branch']
        self.actor = {'login': 'Yaman-A-E', 'id': 123, 'type': 'User'}
        self.remote_head = None
        self.pr = None
        self.comments = []
        self.checks = {}
        self.mutations = []
        self.files = files
        self.merge_sha = 'b' * 40
        self.merge_ok = True
        self.accepted = copy.deepcopy(fixture.api.accepted)
        self.extra_acceptance = {}
        self.reviews = 0
        self.review_status = None
        self.strict = True
        self.duplicate = False
        self.fail_push = False
        self.merge_parents_valid = True

    def identity(self):
        return self.actor

    def review_decision(self, number):
        return self.review_status

    def call(self, path, method='GET', data=None, missing_ok=False):
        if method != 'GET':
            self.mutations.append((path, method, data))
        if path == '/':
            return dict(full_name=REPO, default_branch='main', permissions={'push': True},
                        allow_merge_commit=True)
        if path == '/branches/main/protection':
            return dict(required_status_checks={'strict': self.strict, 'checks': [
                            {'context': name, 'app_id': GITHUB_ACTIONS_APP} for name in HOSTED]},
                        required_pull_request_reviews={'required_approving_review_count': self.reviews},
                        enforce_admins={'enabled': True}, allow_force_pushes={'enabled': False},
                        allow_deletions={'enabled': False}, required_conversation_resolution={'enabled': True})
        if path.startswith('/git/ref/heads/'):
            name = path.removeprefix('/git/ref/heads/')
            sha = self.main if name == 'main' else self.remote_head
            return dict(ref='refs/heads/' + name, object={'type': 'commit', 'sha': sha}) if sha else None
        if path == '/pulls' and method == 'POST':
            self.pr = dict(number=101, state='open', draft=False, body=data['body'],
                           user={'login': self.actor['login']}, html_url=f'https://github.com/{REPO}/pull/101',
                           head={'sha': self.remote_head, 'ref': self.branch, 'repo': {'full_name': REPO}},
                           base={'sha': self.base, 'ref': 'main', 'repo': {'full_name': REPO}},
                           mergeable=True, changed_files=len(self.files))
            return self.pr
        if path == '/pulls/101':
            if method == 'PATCH':
                self.pr.update(data)
            return self.pr
        if path == '/issues/101/comments' and method == 'POST':
            comment = dict(body=data['body'], user={'login': self.actor['login']}, created_at='2026-11-04T00:00:09Z',
                           html_url=f'https://github.com/{REPO}/pull/101#issuecomment-1')
            self.comments.append(comment)
            return comment
        if path == '/pulls/101/merge':
            if not self.merge_ok:
                return {'merged': False}
            if data != {'sha': self.remote_head, 'merge_method': 'merge'}:
                raise AssertionError(data)
            self.pr.update(state='closed', merged=True, merged_at='fixture', merge_commit_sha=self.merge_sha)
            self.main = self.fixture.repo.fixture_main = self.merge_sha
            return {'merged': True, 'sha': self.merge_sha}
        if path == f'/git/commits/{self.merge_sha}':
            return {'parents': [{'sha': self.base}, {'sha': self.remote_head if self.merge_parents_valid else 'bad'}]}
        if path == f'/compare/{self.merge_sha}...{self.main}':
            return {'status': 'identical', 'merge_base_commit': {'sha': self.merge_sha}}
        if path.startswith('/contents/'):
            data = (self.fixture.api.plan if 'task-plan.json' in path else
                    {'accepted': {'8': self.accepted, **self.extra_acceptance}})
            return {'encoding': 'base64', 'content': base64.b64encode(json.dumps(data).encode()).decode()}
        if path == '/issues/11' and self.pr and self.pr.get('merged'):
            return {'state': 'closed', 'state_reason': 'completed'}
        return self.fixture.api.call(path)

    def pages(self, path, key=None):
        if path.startswith('/pulls?head='):
            return [self.pr] if self.pr else []
        if path == '/pulls?state=open&base=main':
            return [{'body': 'Task: #11'}] if self.duplicate else []
        if path == '/rules/branches/main':
            return []
        if path == '/pulls/101/files':
            return [{'filename': path} for path in self.files]
        if path == '/pulls/101/reviews':
            return []
        if path == '/pulls/101/commits':
            return [{'author': {'login': self.actor['login']}}]
        if path == '/issues/101/comments':
            return self.comments
        if path == f'/commits/{self.remote_head}/check-runs?filter=latest' and self.remote_head:
            return self.runs(self.remote_head)
        if path == f'/commits/{self.merge_sha}/check-runs?filter=latest':
            return self.runs(self.merge_sha)
        return self.fixture.api.pages(path, key)

    def runs(self, sha):
        return [dict(name=name, head_sha='stale' if status == 'stale' else sha,
                     app={'slug': 'github-actions', 'id': GITHUB_ACTIONS_APP},
                     started_at='2026-11-04T00:00:10Z', status='completed', conclusion=status)
                for name, status in self.checks.items() if status is not None]

    def push(self, repo, branch, head):
        self.mutations.append(('git push', branch, head))
        if self.fail_push:
            raise Rejected('Feature branch push failed')
        self.remote_head = head


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.fixture = execution.ExecutionTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.repo = self.fixture.repo
        self.repo.git('remote', 'set-url', 'origin', f'https://github.com/{REPO}.git')
        self.repo.git('config', 'core.autocrlf', 'input')
        self.contract = self.fixture.contract
        self.contract['report_path'] = execution.FILE
        self.fixture.write('unrelated.txt', b'preserve local bytes')
        self.contract['existing_changes'] = ['unrelated.txt']
        self.session = self.fixture.start()
        self.fixture.write()
        self.review = self.fixture.review(self.session)
        self.journal = self.repo.root.parent / 'publication.json'
        self.api = FakeGitHub(self.fixture, [execution.FILE])
        self.api.checks = {name: 'success' for name in HOSTED | {'contract-checks'}}
        for name, target in [('trusted_activation', lambda *_: None), ('push_commit', self.api.push)]:
            stub = patch('safe_publish.' + name, target)
            stub.start()
            self.addCleanup(stub.stop)
        stub = patch('lifecycle.State', side_effect=Rejected('Lifecycle activation is unavailable'))
        stub.start()
        self.addCleanup(stub.stop)

    def publish(self, command='PUSHLA', review_id=None):
        return publish(self.repo, self.api, self.contract, self.session, self.review, command,
                       review_id or self.review['review_id'], 'fixture user reviewed exact diff',
                       self.journal, attempts=1, pause=lambda _: None)

    def test_one_command_commits_pushes_creates_pr_merges_and_verifies(self):
        result = self.publish()
        self.assertEqual('MERGED_PENDING_ACCEPTANCE', result['status'])
        self.assertEqual(self.api.merge_sha, result['merge_sha'])
        self.assertEqual('REVIEW_REQUIRED', result['handoff']['status'])
        self.assertEqual('ismail-cevik', result['handoff']['proposed_owner'])
        self.assertFalse(result['rotation_written'])
        self.assertFalse(result['phase_locked'])
        self.assertEqual('Yaman-A-E', result['history']['pr_author'])
        self.assertEqual(b'preserve local bytes', (self.repo.root / 'unrelated.txt').read_bytes())
        self.assertEqual(execution.FILE, self.repo.text('diff', 'HEAD^', 'HEAD', '--name-only'))
        self.assertEqual(1, sum(path == '/pulls/101/merge' for path, _, _ in self.api.mutations))

    def test_missing_wrong_actor_stale_review_and_wrong_remote_block(self):
        for command, review_id, message in [('', None, 'Explicit PUSHLA'),
                                            ('PUSHLA', 'stale', 'Wrong review')]:
            with self.assertRaisesRegex(Rejected, message):
                self.publish(command, review_id)
        self.api.actor['login'] = 'caferkilinc'
        with self.assertRaisesRegex(Rejected, 'Authenticated GitHub developer'):
            self.publish()
        self.api.actor['login'] = 'Yaman-A-E'
        self.repo.git('remote', 'set-url', '--push', 'origin', 'https://github.com/example/fork.git')
        with self.assertRaisesRegex(Rejected, 'Wrong or ambiguous'):
            self.publish()
        self.assertEqual([], self.api.mutations)

    def test_changed_diff_unauthorized_paths_and_protected_inputs_block(self):
        self.fixture.write(content=b'changed after review')
        with self.assertRaisesRegex(Rejected, 'Stale approval'):
            self.publish()
        self.fixture.write('unauthorized.py')
        with self.assertRaisesRegex(Rejected, 'Out-of-task path'):
            self.publish()
        self.fixture.write(execution.FROZEN_FILE, b'changed frozen bytes')
        # Protected-file guard is independent of the unrelated file.
        (self.repo.root / 'unauthorized.py').unlink()
        with self.assertRaisesRegex(Rejected, 'Protected path changed'):
            self.publish()
        self.assertFalse(self.journal.exists())

    def test_failed_push_preserves_commit_and_retry_uses_same_commit(self):
        self.api.fail_push = True
        with self.assertRaisesRegex(Rejected, 'Feature branch push failed'):
            self.publish()
        head = self.repo.text('rev-parse', 'HEAD')
        self.assertNotEqual(self.api.base, head)
        self.assertIsNone(self.api.pr)
        self.api.fail_push = False
        self.api.checks['contract-checks'] = None
        self.assertEqual('PUBLISHED_PENDING_CI', self.publish()['status'])
        self.assertEqual(head, self.api.remote_head)
        self.assertEqual(head, self.repo.text('rev-parse', 'HEAD'))

    def test_missing_or_stale_ci_stays_pending_and_does_not_duplicate_pr(self):
        self.api.checks['contract-checks'] = None
        self.assertIn('contract-checks', self.publish()['pending_checks'])
        self.api.checks['contract-checks'] = 'stale'
        self.assertIn('contract-checks', self.publish()['pending_checks'])
        self.assertEqual(1, sum(path == '/pulls' for path, _, _ in self.api.mutations))
        self.assertFalse(any(path.endswith('/merge') for path, _, _ in self.api.mutations))

    def test_failed_skipped_ci_and_missing_independent_review_block(self):
        for state in ('failure', 'skipped'):
            self.api.checks['contract-checks'] = state
            with self.assertRaisesRegex(Rejected, 'Required check failed'):
                self.publish()
        self.api.checks['contract-checks'] = 'success'
        self.api.reviews = 1
        with self.assertRaisesRegex(Rejected, 'Required independent GitHub review'):
            self.publish()
        self.assertFalse(any(path.endswith('/merge') for path, _, _ in self.api.mutations))

    def test_merge_failure_and_mismatched_post_merge_evidence(self):
        self.api.merge_ok = False
        with self.assertRaisesRegex(Rejected, 'GitHub declined the merge'):
            self.publish()
        self.api.merge_ok = True
        self.api.merge_parents_valid = False
        result = self.publish()
        self.assertEqual('MERGED_PENDING_ACCEPTANCE', result['status'])
        self.assertIn('Merge parents differ', result['blocker'])

    def test_existing_acceptance_is_idempotent_and_does_not_rewrite_history(self):
        first = self.publish()
        self.api.extra_acceptance['11'] = first['handoff_record']
        again = self.publish()
        self.assertEqual('ACCEPTED', again['status'])
        self.assertEqual('ALREADY_ACCEPTED', again['handoff']['status'])
        self.assertFalse(again['handoff']['advance'])
        self.assertFalse(again['phase_locked'])
        self.assertEqual(1, sum(path == '/pulls/101/merge' for path, _, _ in self.api.mutations))
        self.assertEqual('', self.repo.text('diff', '--', '.github/acceptance.json', '.github/task-plan.json'))

    def test_duplicate_task_pr_and_missing_strict_protection_block(self):
        self.api.strict = False
        with self.assertRaisesRegex(Rejected, 'Classic main protection'):
            active_protection(self.api)
        self.api.strict = True
        self.api.duplicate = True
        with self.assertRaisesRegex(Rejected, 'already claims this task'):
            self.publish()
        self.assertEqual([], self.api.mutations)

    def test_old_gate_results_before_authenticated_approval_are_pending(self):
        original = self.api.runs
        def old_gate(sha):
            runs = original(sha)
            for run in runs:
                if run['name'] == 'merge-readiness':
                    run.update(started_at='2026-11-04T00:00:01Z', conclusion='failure')
            return runs
        with patch.object(self.api, 'runs', side_effect=old_gate):
            result = self.publish()
        self.assertIn('merge-readiness', result['pending_checks'])
        self.assertFalse(any(path.endswith('/merge') for path, _, _ in self.api.mutations))

    def test_candidate_cannot_supply_its_own_activation(self):
        with self.assertRaisesRegex(Rejected, 'Missing required source'):
            trusted_activation(self.repo, self.api.base)
        self.assertEqual([], self.api.mutations)

    def test_push_has_fixed_refspec_tls_and_no_token_in_command(self):
        self.api.remote_head = 'a' * 40
        with patch.object(self.repo, 'text', return_value=f'https://github.com/{REPO}.git'), patch.dict(
                'os.environ', {'GH_TOKEN': 'fixture-token'}), patch(
                'safe_publish.subprocess.run') as run:
            run.return_value.returncode = 0
            push_commit(self.repo, self.api.branch, self.api.remote_head)
            argv = run.call_args.args[0]
            self.assertEqual(f"{self.api.remote_head}:refs/heads/{self.api.branch}", argv[-1])
            self.assertNotIn('--force', argv)
            self.assertNotIn('fixture-token', ' '.join(argv))
            self.assertIn('http.sslVerify=true', argv)
            self.assertTrue(run.call_args.kwargs['env']['GIT_CONFIG_VALUE_1'].startswith('Authorization: Basic '))

    def test_post_merge_checks_pending_keep_acceptance_and_phase_unwritten(self):
        original = self.api.runs
        with patch.object(self.api, 'runs', side_effect=lambda sha: [
                run for run in original(sha) if sha != self.api.merge_sha or run['name'] != 'pilot-checks']):
            result = self.publish()
        self.assertIn('pilot-checks', result['pending_checks'])
        self.assertFalse(result['rotation_written'])
        self.assertFalse(result['phase_locked'])


if __name__ == '__main__':
    unittest.main()
