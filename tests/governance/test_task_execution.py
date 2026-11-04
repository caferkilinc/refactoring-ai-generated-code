"""Local execution guards using real temporary Git worktrees and read-only API fixtures."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts/governance'))
from gate import Rejected
from task_execution import REPO, Repository, decide, record_decision, review, start


BRANCH = 'feature/11-contract-fixture'
FILE = 'docs/contracts/mig03-fixture.md'
FROZEN_FILE = 'experiments/java-pilot/manifests/v0-source.json'


class FixtureRepository(Repository):
    def live_main(self):
        return self.fixture_main


class ReadOnlyAPI:
    def __init__(self, accepted, plan):
        self.accepted = accepted['8']
        self.plan = plan
        self.native = [{'number': 8}]
        self.calls = []

    def call(self, path):
        self.calls.append(path)
        if path == '/issues/11':
            return {'state': 'open'}
        if path == '/issues/8':
            return {'state': 'closed', 'state_reason': 'completed'}
        if path == '/pulls/44':
            return dict(number=44, merged_at='observed', body='Task: #8\nPlan: F00-PLAN',
                        head={'ref': 'docs/8-freeze-evidence-protocol', 'sha': self.accepted['head_sha']},
                        base={'ref': 'main', 'repo': {'full_name': REPO}}, changed_files=1)
        raise AssertionError(path)

    def pages(self, path, key=None):
        self.calls.append(path)
        if path == '/issues/11/dependencies/blocked_by':
            return self.native
        if path == '/pulls/44/files':
            return [{'filename': 'docs/DECISIONS/fixture.md'}]
        if path == '/issues/44/comments':
            return [{'user': {'login': 'cakarburkayy'},
                     'body': 'GENESIS-OWNER-APPROVED: ' + self.accepted['head_sha']}]
        if path == f"/commits/{self.accepted['ci_sha']}/check-runs?filter=latest":
            task = next(t for t in self.plan['tasks'] if t['plan_id'] == 'F00-PLAN')
            return [dict(name=name, status='completed', conclusion='success',
                         app={'slug': 'github-actions'}) for name in task['required_checks']]
        raise AssertionError(path)


class ExecutionTests(unittest.TestCase):
    def setUp(self):
        temp_parent = Path(tempfile.gettempdir()).resolve(strict=True)
        temp = tempfile.TemporaryDirectory(prefix='genesis-execution-', dir=temp_parent)
        directory = Path(temp.name).resolve(strict=True)
        self.assertEqual(directory.parent, temp_parent)
        self.addCleanup(temp.cleanup)
        checkout = directory / 'checkout'
        checkout.mkdir()
        self.repo = FixtureRepository(checkout)
        self.repo.git('init', '-q')
        self.repo.git('remote', 'add', 'origin', 'https://github.com/example/not-genesis.git')
        self.repo.git('switch', '-q', '-c', BRANCH)
        plan = json.loads((ROOT / '.github/task-plan.json').read_bytes())
        plan['sequential_execution'].update(active_owner='Yaman-A-E', active_task_plan_id='F02-CONTRACT',
                                            rotation_index=2, next_owner_if_accepted='ismail-cevik',
                                            handoff_confirmed=False)
        accepted = {'8': {'pr': 44, 'head_sha': 'a' * 40, 'ci_sha': 'a' * 40,
                          'evidence': ['https://github.com/' + REPO + '/pull/44']}}
        self.write('.github/task-plan.json', json.dumps(plan).encode())
        self.write('.github/acceptance.json', json.dumps({'accepted': accepted}).encode())
        for path in ('AGENTS.md', 'docs/SRS.md', '.agents/skills/development-handoff/SKILL.md', FROZEN_FILE):
            self.write(path, b'fixture source\n')
        self.repo.git('add', '--', '.')
        self.repo.git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                      '-c', 'commit.gpgsign=false', 'commit', '-qm', 'Disposable fixture')
        self.repo.fixture_main = self.repo.text('rev-parse', 'HEAD')
        self.api = ReadOnlyAPI(accepted, plan)
        task = next(t for t in plan['tasks'] if t['plan_id'] == 'F02-CONTRACT')
        command = [sys.executable, '-B', '-c', 'raise SystemExit(0)']
        self.contract = dict(repository=REPO, task_id='F02-CONTRACT', task_title=task['title'],
                             task_type='product', authorized_developer='Yaman-A-E', branch=BRANCH,
                             base_revision=self.repo.fixture_main, source_main_sha=self.repo.fixture_main,
                             objective='Fixture only',
                             authorization_reference='fixture human authorization',
                             prerequisites=['F00-PLAN'], required_context=['docs/SRS.md'],
                             allowed_paths=['docs/contracts/'], protected_paths=[],
                             acceptance_criteria=['fixture criterion'], stop_conditions=['on failure'],
                             verification_requirements={name: command for name in task['required_checks']})
        self.session_file = directory / 'session.json'

    def write(self, name=FILE, content=b'fixture\n'):
        path = self.repo.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)

    def start(self):
        return start(self.repo, self.contract, self.api)

    def review(self, session):
        return review(self.repo, self.contract, session, self.api)

    def decision(self, session, reviewed, choice='ONAYLA', developer='Yaman-A-E',
                 reference='fixture decision for exact review', review_id=None):
        result = decide(self.repo, self.contract, session, reviewed, review_id or reviewed['review_id'],
                        choice, developer, reference, self.api)
        record_decision(self.repo, self.session_file, reviewed, result)
        return result

    def test_valid_task_preserves_existing_files_and_reaches_human_review(self):
        self.write('user-notes.txt', b'keep these bytes')
        self.contract['existing_changes'] = ['user-notes.txt']
        session = self.start()
        self.assertEqual('TASK_AUTHORIZED', session['status'])
        self.write()
        result = self.review(session)
        self.assertEqual('HUMAN_APPROVAL_PENDING', result['status'])
        self.assertEqual([FILE], result['changed_files'])
        self.assertFalse(result['publication_authorized'])
        self.assertTrue(all(check['exit_code'] == 0 for check in result['results'].values()))
        self.assertEqual(b'keep these bytes', (self.repo.root / 'user-notes.txt').read_bytes())
        self.assertEqual(self.repo.fixture_main, self.repo.text('rev-parse', 'HEAD'))

    def test_wrong_developer_and_unknown_task_rejected(self):
        self.contract['authorized_developer'] = 'caferkilinc'
        with self.assertRaisesRegex(Rejected, 'Wrong active task or developer'):
            self.start()
        self.contract['task_id'] = 'UNKNOWN'
        with self.assertRaisesRegex(Rejected, 'Unknown registered product task'):
            self.start()

    def test_missing_prerequisite_and_context_block(self):
        self.api.native = []
        with self.assertRaisesRegex(Rejected, 'Native dependencies disagree'):
            self.start()
        self.contract['required_context'] = ['docs/absent-fixture.md']
        with self.assertRaisesRegex(Rejected, 'Missing required source'):
            self.start()

    def test_wrong_canonical_origin_and_stale_baselines_block(self):
        with self.assertRaisesRegex(Rejected, 'Wrong canonical origin'):
            start(Repository(self.repo.root), self.contract, self.api)
        self.contract['source_main_sha'] = '0' * 40
        with self.assertRaisesRegex(Rejected, 'Stale canonical main'):
            self.start()
        self.contract.update(source_main_sha=self.repo.fixture_main, base_revision='0' * 40)
        with self.assertRaisesRegex(Rejected, 'Wrong working branch or base'):
            self.start()

    def test_out_of_scope_contract_and_diff_rejected(self):
        self.contract['allowed_paths'] = ['backend/']
        with self.assertRaisesRegex(Rejected, 'Out-of-task path'):
            self.start()
        self.contract['allowed_paths'] = ['docs/contracts/']
        session = self.start()
        self.write('unexpected.py')
        with self.assertRaisesRegex(Rejected, 'Out-of-task path: unexpected.py'):
            self.review(session)

    def test_protected_input_change_and_unknown_start_block(self):
        session = self.start()
        self.write(FROZEN_FILE, b'not the original manifest')
        with self.assertRaisesRegex(Rejected, 'Protected path changed'):
            self.review(session)
        with self.assertRaisesRegex(Rejected, 'Unexpected starting changes'):
            self.start()

    def test_starting_changes_cannot_be_overwritten(self):
        self.write('user-notes.txt')
        self.contract['existing_changes'] = ['user-notes.txt']
        session = self.start()
        self.write('user-notes.txt', b'changed')
        with self.assertRaisesRegex(Rejected, 'Existing developer work changed'):
            self.review(session)

    def test_nonzero_and_missing_checks_prevent_approval(self):
        self.contract['verification_requirements']['contract-checks'] = [
            sys.executable, '-B', '-c', 'raise SystemExit(7)']
        del self.contract['verification_requirements']['security-checks']
        session = self.start()
        self.write()
        result = self.review(session)
        self.assertEqual('BLOCKED', result['status'])
        self.assertEqual(('FAIL', 7), (result['results']['contract-checks']['status'],
                                      result['results']['contract-checks']['exit_code']))
        self.assertEqual('NOT_RUN', result['results']['security-checks']['status'])
        with self.assertRaisesRegex(Rejected, 'Mandatory verification has not passed'):
            self.decision(session, result)

    def test_review_rejects_commands_that_mutate_checkout(self):
        self.contract['verification_requirements']['contract-checks'] = [
            sys.executable, '-B', '-c', "from pathlib import Path; Path('unexpected.out').touch()"]
        session = self.start()
        self.write()
        with self.assertRaisesRegex(Rejected, 'Verification changed the review snapshot'):
            self.review(session)

    def test_review_identity_and_changed_content_invalidate_approval(self):
        session = self.start()
        self.write()
        result = self.review(session)
        with self.assertRaisesRegex(Rejected, 'Explicit developer decision'):
            self.decision(session, result, developer='caferkilinc')
        with self.assertRaisesRegex(Rejected, 'Review record does not match'):
            self.decision(session, result, review_id='old-id')
        self.write(content=b'edited after review')
        with self.assertRaisesRegex(Rejected, 'Stale approval'):
            self.decision(session, result)

    def test_rejection_closes_review_and_fresh_review_still_requires_human(self):
        session = self.start()
        self.write()
        result = self.review(session)
        rejected = self.decision(session, result, 'REDDET')
        self.assertEqual('REJECTED', rejected['status'])
        self.assertFalse(rejected['publication_authorized'])
        with self.assertRaisesRegex(Rejected, 'A decision for this review already exists'):
            self.decision(session, result)
        self.write(content=b'new review bytes')
        fresh = self.review(session)
        self.assertEqual('HUMAN_APPROVAL_PENDING', fresh['status'])
        approved = self.decision(session, fresh)
        self.assertEqual('APPROVED_FOR_SEPARATE_PUBLICATION_REVIEW', approved['status'])
        self.assertFalse(approved['publication_authorized'])

    def test_governance_migration_cannot_claim_product_scope_or_advance_rotation(self):
        self.contract.update(task_id='MIG-03', task_type='migration', prerequisites=[],
                             authorized_developer='cakarburkayy')
        self.contract['protected_authorization'] = {
            key: self.contract[key] for key in
            ('repository', 'task_id', 'authorized_developer', 'branch', 'base_revision')}
        self.contract['protected_authorization'].update(
            paths=['docs/contracts/mig03-fixture.md'], reference='fixture owner evidence')
        with self.assertRaisesRegex(Rejected, 'Unauthorized migration scope'):
            self.start()
        self.assertEqual(self.repo.fixture_main, self.repo.text('rev-parse', 'HEAD'))
        self.assertEqual('', self.repo.text('status', '--porcelain=v1'))
        self.assertFalse((self.repo.root / 'docs/history/GENESIS_EVENTS.jsonl').exists())

    def test_migration_uses_local_predecessors_without_product_acceptance(self):
        self.repo.git('switch', '-q', '-c', 'chore/1-genesis-v3-phase1')
        report = 'docs/reports/MIG-03.md'
        self.contract.update(task_id='MIG-03', task_type='migration', prerequisites=[],
                             branch='chore/1-genesis-v3-phase1', authorized_developer='cakarburkayy',
                             allowed_paths=[report])
        self.contract['protected_authorization'] = {
            key: self.contract[key] for key in
            ('repository', 'task_id', 'authorized_developer', 'branch', 'base_revision')}
        self.contract['protected_authorization'].update(paths=[report], reference='fixture owner evidence')
        with self.assertRaisesRegex(Rejected, 'Missing MIG-02 prerequisite'):
            self.start()
        existing = [f'.agents/skills/{name}/SKILL.md' for name in
                    ('repo-bootstrap', 'task-context', 'verification')]
        for path in existing:
            self.write(path)
        self.contract['existing_changes'] = existing
        session = self.start()
        self.write(report)
        result = self.review(session)
        self.assertEqual('HUMAN_APPROVAL_PENDING', result['status'])
        self.assertEqual([], self.api.calls)
        self.assertEqual(self.repo.fixture_main, self.repo.text('rev-parse', 'HEAD'))
        self.assertEqual('', self.repo.text('diff', '--', '.github'))
        self.assertFalse((self.repo.root / 'docs/history/GENESIS_EVENTS.jsonl').exists())


if __name__ == '__main__':
    unittest.main()
