"""Exercise publication and protected records with disposable Git and GitHub evidence."""
import copy
import json
import unittest
from unittest.mock import patch

import test_task_execution as execution
from test_safe_publish import FakeGitHub
from lifecycle import (ACCEPTANCE, HISTORY, MIGRATIONS, OWNER, PLAN, State, append_events, digest, event, events_from,
                       phase_records, prepare_acceptance, prepare_correction, prepare_phase,
                       verify_candidate)
from next_step import (HANDOFF_INTENT, POLICY, PRODUCT_DOCS, SKILLS, archive_prompt,
                       post_migration_handoff, render_prompt, validate_prompt)
from safe_publish import HOSTED, REPO, publish
from gate import Rejected


NOW = '2026-11-04T00:01:00Z'
URL = f'https://github.com/{REPO}'


class LifecycleAPI(FakeGitHub):
    def __init__(self, fixture):
        super().__init__(fixture, [execution.FILE])
        self.decisions = []
        self.checks = {name: 'success' for name in HOSTED | {'contract-checks'}}

    def call(self, path, method='GET', data=None, missing_ok=False):
        if path == '/pulls/101/merge' and method == 'PUT':
            repo = self.fixture.repo
            tree = repo.text('rev-parse', self.remote_head + '^{tree}')
            self.merge_sha = repo.text('commit-tree', tree, '-p', self.base, '-p', self.remote_head,
                                       '-m', 'Verified fixture merge')
            result = super().call(path, method, data, missing_ok)
            self.pr.update(merged_at='2026-11-04T00:00:20Z', merged_by={'login': 'fixture-merger'})
            return result
        if path.startswith('/compare/'):
            old, new = path.removeprefix('/compare/').split('...')
            common = self.fixture.repo.text('merge-base', old, new)
            return dict(status='identical' if old == new else 'ahead', merge_base_commit={'sha': common})
        if path == '/pulls/44':
            return dict(super().call(path, method, data, missing_ok),
                        merge_commit_sha=self.base, html_url=URL + '/pull/44')
        if path == '/issues/12':
            return {'state': 'open'}
        return super().call(path, method, data, missing_ok)

    def pages(self, path, key=None):
        if path == '/pulls?state=closed&base=main':
            return [self.pr] if self.pr and self.pr.get('merged') else []
        if path == '/issues/12/dependencies/blocked_by':
            return [{'number': 11}]
        if path == '/issues/101/comments':
            return self.comments
        if path == '/pulls/101/reviews':
            return [{'user': {'login': 'fixture-reviewer'}, 'state': 'APPROVED',
                     'commit_id': self.remote_head}]
        if path == f'/commits/{self.main}/check-runs?filter=latest':
            return self.runs(self.main)
        return super().pages(path, key)


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.fixture = execution.ExecutionTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.repo = self.fixture.repo
        self.repo.git('config', 'user.name', 'Fixture')
        self.repo.git('config', 'user.email', 'fixture@example.invalid')
        self.repo.git('config', 'commit.gpgsign', 'false')
        self.repo.git('remote', 'set-url', 'origin', URL + '.git')
        plan = self.fixture.api.plan
        plan['tasks'] = [task for task in plan['tasks'] if task['issue_number'] in (8, 11, 12)]
        plan['tasks'][-1].update(phase='F03', dependencies=['F02-CONTRACT'], dependency_issues=[11])
        self.fixture.write(PLAN, json.dumps(plan).encode())
        self.fixture.write(ACCEPTANCE, json.dumps({'schema_version': 1,
                                                   'accepted': {'8': self.fixture.api.accepted}}).encode())
        for path in (*PRODUCT_DOCS, *SKILLS, POLICY):
            self.fixture.write(path, b'Fixture product or governance source\n')
        for name in ('lifecycle.py', 'next_step.py'):
            path = 'scripts/governance/' + name
            self.fixture.write(path, (execution.ROOT / path).read_bytes())
        self.repo.git('add', '--', '.')
        self.repo.git('commit', '--amend', '--no-edit', '-q')
        base = self.repo.fixture_main = self.repo.text('rev-parse', 'HEAD')
        self.fixture.contract.update(base_revision=base, source_main_sha=base, report_path=execution.FILE)
        self.api = LifecycleAPI(self.fixture)
        for name, target in [('trusted_activation', lambda *_: None), ('push_commit', self.api.push)]:
            stub = patch('safe_publish.' + name, target)
            stub.start()
            self.addCleanup(stub.stop)

    def publish(self):
        contract = self.fixture.contract
        session = self.fixture.start()
        self.fixture.write()
        reviewed = self.fixture.review(session)
        return publish(self.repo, self.api, contract, session, reviewed, 'PUSHLA', reviewed['review_id'],
                       'fixture decision for exact diff', self.repo.root.parent / 'journal.json',
                       attempts=1, pause=lambda _: None)

    def proposal(self, state=None):
        return prepare_acceptance(state or State(self.repo, self.api), 101, self.api.remote_head,
                                  self.api.base, NOW)

    def integrate(self, proposal):
        state = State(self.repo, self.api)
        # The fake integration uses a real Git candidate. No actual push, PR or merge is performed.
        self.repo.git('switch', '--detach', state.main)
        for path, content in proposal['files'].items():
            self.fixture.write(path, content.encode('utf-8'))
        self.repo.git('add', '--', *proposal['files'])
        self.repo.git('commit', '-qm', 'Integrate fixture protected records')
        revision = self.repo.text('rev-parse', 'HEAD')
        verify_candidate(state, proposal, revision)
        self.api.main = self.repo.fixture_main = revision

    def phase(self, action, phase='F02', reason=None):
        state = State(self.repo, self.api)
        evidence = URL + '/issues/11'
        previous = phase_records(state.events).get(phase, {}).get('event_id')
        marker = 'GENESIS-PHASE-DECISION: ' + REPO + ' ' + digest(
            [REPO, state.main, action, phase, evidence, reason, previous, None])
        self.api.comments.append(dict(user={'login': OWNER}, body=marker, created_at=NOW,
                                      html_url=URL + '/issues/11#issuecomment-1'))
        # Issue and PR numbers occupy different evidence roles.
        original = self.api.pages
        with patch.object(self.api, 'pages', side_effect=lambda path, *args, **kwargs:
                          self.api.comments if path == '/issues/11/comments'
                          else original(path, *args, **kwargs)):
            return prepare_phase(state, action, phase, evidence, reason, NOW)

    def install_intent(self, selected=None, *, migration_accepted=False):
        state = State(self.repo, self.api)
        intent = json.loads((execution.ROOT / HANDOFF_INTENT).read_bytes())
        if selected:
            intent.update(reconciled_task_id=selected, reconciliation_evidence=URL + '/issues/1')
        content = json.dumps(intent) + '\n'
        files = {}
        if not self.repo.text('ls-tree', state.main, HANDOFF_INTENT) or self.repo.blob(
                state.main, HANDOFF_INTENT) != content.encode():
            files[HANDOFF_INTENT] = content
        if migration_accepted:
            entries = [event('MIGRATION_ACCEPTED', 'migration_phase', phase, phase, self.api.base, 1,
                             [URL + '/issues/1'], NOW, actor=OWNER, role='project_owner')
                       for phase in MIGRATIONS]
            files[HISTORY] = append_events(state.raw_history, entries)
        self.integrate(dict(source_main_sha=state.main, files=files))

    def test_end_to_end_single_command_through_verified_next_prompt(self):
        published = self.publish()
        prepared = published['acceptance_transaction']
        self.assertEqual('MERGED_PENDING_ACCEPTANCE', prepared['status'])
        self.assertEqual({PLAN, ACCEPTANCE, HISTORY}, set(prepared['files']))
        self.assertEqual('F02-CONTRACT', State(self.repo, self.api).rotation['active_task_plan_id'])
        with self.assertRaises(Rejected):
            render_prompt(State(self.repo, self.api))
        self.integrate(prepared)
        retry = self.proposal()
        self.assertEqual('ALREADY_ACCEPTED', retry['status'])
        self.assertEqual({}, retry['files'])
        self.assertEqual('ELIGIBLE_PENDING_OWNER_LOCK_RECORD', retry['phase_evaluation']['status'])
        state = State(self.repo, self.api)
        self.assertEqual(3, state.rotation['rotation_index'])
        self.assertEqual(self.fixture.api.accepted, state.accepted['8'])
        self.assertEqual(4, len(state.events))
        accepted = next(entry for entry in state.events.values() if entry['event_type'] == 'TASK_ACCEPTED')
        roles = accepted['contributors']
        self.assertIsNone(roles['actual_implementer'])
        self.assertEqual(['fixture-reviewer'], roles['reviewer'])
        self.assertEqual('Yaman-A-E', roles['human_approver'])
        lock = self.phase('lock')
        self.integrate(lock)
        state = State(self.repo, self.api)
        self.assertEqual('LOCKED', phase_records(state.events)['F02']['status'])
        self.assertEqual('ALREADY_LOCKED', self.phase('lock')['status'])
        self.assertEqual(3, state.rotation['rotation_index'])
        self.install_intent('F02-CONTRACT', migration_accepted=True)
        state = State(self.repo, self.api)
        prompt = render_prompt(state)
        self.assertIn('F02-STATE', prompt)
        self.assertIn('ismail-cevik', prompt)
        self.assertIn(state.main, prompt)
        self.assertIn('F02-CONTRACT via PR #101', prompt)
        self.assertIn(PLAN, prompt)
        validate_prompt(state, prompt.encode())
        with self.assertRaisesRegex(Rejected, 'Invalid or stale prompt'):
            validate_prompt(state, prompt.replace(state.main, 'a' * 40).encode())
        archive = archive_prompt(state, prompt)
        self.assertEqual(prompt.encode(), (self.repo.root / archive).read_bytes())
        with self.assertRaisesRegex(Rejected, 'already exists'):
            archive_prompt(state, prompt)
        original = state.raw_history
        with patch.object(self.api, 'pages', return_value=[]):
            with self.assertRaisesRegex(Rejected, 'Missing exact project owner decision'):
                prepare_phase(state, 'reopen', 'F02', URL + '/issues/11', 'new finding', NOW)
        self.integrate(self.phase('reopen', reason='verified new finding'))
        state = State(self.repo, self.api)
        self.assertTrue(state.raw_history.startswith(original))
        self.assertEqual('REOPENED', phase_records(state.events)['F02']['status'])
        self.assertEqual(set(MIGRATIONS), {key for key in phase_records(state.events)
                                          if key.startswith('MIG-')})
        target = next(iter(state.events))
        reason, evidence = 'Add separately verified attribution evidence', URL + '/issues/11'
        with patch.object(self.api, 'pages', return_value=[]):
            with self.assertRaisesRegex(Rejected, 'Missing exact owner correction'):
                prepare_correction(state, target, reason, evidence, NOW)
        marker = (f'GENESIS-HISTORY-CORRECTION: {REPO} {state.main} '
                  + digest([target, reason, evidence]))
        decision = dict(user={'login': OWNER}, body=marker, created_at=NOW,
                        html_url=evidence + '#issuecomment-2')
        with patch.object(self.api, 'pages', return_value=[decision]):
            correction = prepare_correction(state, target, reason, evidence, NOW)
        self.integrate(correction)
        state = State(self.repo, self.api)
        self.assertEqual('ALREADY_RECORDED', prepare_correction(
            state, target, reason, evidence, NOW)['status'])
        self.assertIn(target, state.events)

    def test_changed_source_missing_approval_failed_ci_and_incomplete_phase(self):
        self.publish()
        with self.assertRaisesRegex(Rejected, 'Incomplete phase'):
            self.phase('lock')
        state = State(self.repo, self.api)
        self.api.main = self.repo.fixture_main = self.api.base
        with self.assertRaisesRegex(Rejected, 'Trusted main moved'):
            state.recheck()
        self.api.main = self.repo.fixture_main = self.api.merge_sha
        approvals = self.api.comments[:]
        self.api.comments.clear()
        with self.assertRaisesRegex(Rejected, 'Missing pre-merge developer approval'):
            self.proposal()
        self.api.comments[:] = approvals
        self.api.checks['merge-readiness'] = None
        with self.assertRaisesRegex(Rejected, 'Missing/failed.*merge-readiness'):
            self.proposal()
        self.api.checks['merge-readiness'] = 'failure'
        with self.assertRaisesRegex(Rejected, 'Required check failed'):
            self.proposal()

    def test_conflicting_acceptance_and_history_fail_closed(self):
        self.publish()
        proposal = self.proposal()
        self.integrate(proposal)
        self.api.pr['head']['sha'] = self.api.remote_head = 'd' * 40
        with self.assertRaisesRegex(Rejected, 'Conflicting canonical acceptance'):
            self.proposal()
        raw = proposal['files'][HISTORY].encode()
        first = next(iter(events_from(raw).values()))
        self.assertEqual(raw.decode(), append_events(raw, [dict(first, recorded_at=NOW)]))
        with self.assertRaisesRegex(Rejected, 'Conflicting history'):
            append_events(raw, [dict(first, actor_id='someone-else')])
        bad = event('CORRECTION_RECORDED', 'task', 'F02-CONTRACT', 'correction', 'a' * 40, None,
                    [URL], NOW, actor=OWNER, role='project_owner', reason='reason', previous_event='missing')
        with self.assertRaisesRegex(Rejected, 'existing event'):
            append_events(raw, [bad])

    def test_canonical_rotation_and_next_dependency_must_agree(self):
        self.publish()
        self.integrate(self.proposal())
        state = State(self.repo, self.api)
        state.rotation['rotation_index'] = 0
        with self.assertRaisesRegex(Rejected, 'history and rotation disagree'):
            render_prompt(state)
        state = State(self.repo, self.api)
        state.tasks['F02-STATE']['dependencies'].append('F00-PLAN')
        del state.accepted['8']
        with self.assertRaisesRegex(Rejected, 'dependencies conflict'):
            render_prompt(state)

    def test_migration_acceptance_has_separate_authority_and_no_product_rotation(self):
        self.publish()
        self.api.pr['head']['ref'] = 'chore/1-genesis-v3-phase1'
        original = self.api.pages
        for phase, expected in [('MIG-02', 'Earlier migration acceptance'), ('MIG-01', None)]:
            state = State(self.repo, self.api)
            evidence = URL + '/issues/1'
            key = digest([REPO, state.main, 'migration-accept', phase, evidence, None, None, 101])
            decision = dict(user={'login': OWNER}, body=f'GENESIS-PHASE-DECISION: {REPO} {key}',
                            created_at=NOW, html_url=evidence + '#issuecomment-3')
            with patch.object(self.api, 'pages', side_effect=lambda path, *args, **kwargs:
                              [decision] if path == '/issues/1/comments'
                              else original(path, *args, **kwargs)):
                if expected:
                    with self.assertRaisesRegex(Rejected, expected):
                        prepare_phase(state, 'migration-accept', phase, evidence, None, NOW, 101)
                else:
                    proposal = prepare_phase(state, 'migration-accept', phase, evidence, None, NOW, 101)
        self.assertEqual({HISTORY}, set(proposal['files']))
        self.integrate(proposal)
        state = State(self.repo, self.api)
        self.assertEqual(2, state.rotation['rotation_index'])
        self.assertEqual('F02-CONTRACT', state.rotation['active_task_plan_id'])
        self.assertIn('acceptance', phase_records(state.events)['MIG-01'])

    def test_alperen_handoff_requires_migration_acceptance_and_exact_reconciliation(self):
        self.install_intent()
        state = State(self.repo, self.api)
        with self.assertRaisesRegex(Rejected, 'Alperen.*awaits trusted migration acceptance'):
            render_prompt(state)
        self.install_intent(migration_accepted=True)
        state = State(self.repo, self.api)
        with self.assertRaisesRegex(Rejected, 'exact protected task decision.*F02-CONTRACT / #11'):
            render_prompt(state)
        self.install_intent('F02-STATE')
        state = State(self.repo, self.api)
        with self.assertRaisesRegex(Rejected, 'Reconcile F02-CONTRACT.*F02-STATE'):
            render_prompt(state)
        self.assertEqual(2, state.rotation['rotation_index'])
        self.assertEqual('Yaman-A-E', state.rotation['active_owner'])
        self.assertEqual({'8'}, set(state.accepted))
        self.install_intent('F02-CONTRACT')
        state = State(self.repo, self.api)
        self.assertIsNone(post_migration_handoff(state, phase_records(state.events)))


if __name__ == '__main__':
    unittest.main()
