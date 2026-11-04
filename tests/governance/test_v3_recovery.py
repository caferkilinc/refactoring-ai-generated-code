"""Recovery sequencing tests for the separately approved historical repair."""
import copy
import unittest
from unittest.mock import patch

import test_v3_activation as original
from v3_activation import (BOOTSTRAP, BRANCH, CHECKOUT, HOTFIX_PATHS, INITIAL_BOOTSTRAP, OWNER,
                           REPAIR_BRANCH, REPAIR_MERGE, REPO, WORKFLOWS,
                           CandidateChecks, checkout_sha, current_pr, hotfix_marker, verify, verify_hotfix)
import gate


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.fixture = original.ActivationTests()
        self.fixture.setUp()
        self.migration = self.fixture.pr
        self.migration['number'] = 49
        self.grant = self.fixture.grant
        self.grant.update(pr=49, prior_bootstrap='f' * 40, repair=dict(
            pr=48, author='Yaman-A-E', head='d' * 40, accepted_pr=45,
            accepted_head=self.fixture.accepted['9']['head_sha'], paths=['repair-file']))
        self.repair = copy.deepcopy(self.migration)
        self.repair.update(number=48, body='Task: #9\nPlan: F00-V0', changed_files=1,
                           user={'login': 'Yaman-A-E'})
        self.repair['head'].update(ref=REPAIR_BRANCH, sha=self.grant['repair']['head'])
        self.api = original.API(self.fixture)

    def test_base_snapshot_does_not_override_independently_verified_main(self):
        expected = 'e' * 40
        ref = {'ref': 'refs/heads/main', 'object': {'type': 'commit', 'sha': expected}}
        responses = {'/git/ref/heads/main': ref, '/pulls/49': self.migration}
        with patch.object(self.api, 'call', side_effect=responses.__getitem__):
            pr = current_pr(self.api, 49, self.migration['head']['sha'], expected)
            self.assertEqual(expected, pr['base']['sha'])
            self.assertNotEqual(expected, self.migration['base']['sha'])
            with self.assertRaisesRegex(gate.Rejected, 'Trusted main moved'):
                current_pr(self.api, 49, self.migration['head']['sha'], '0' * 40)

    def test_repair_requires_its_own_current_owner_approval_and_original_acceptance(self):
        self.fixture.files = [{'filename': 'repair-file'}]
        self.fixture.native = [{'number': 8}]
        issue = {'state': 'closed', 'state_reason': 'completed'}
        with patch.object(self.api, 'call', side_effect=lambda path: issue if path == '/issues/9'
                          else {'parents': [{'sha': self.grant['prior_bootstrap']}]}), patch(
                              'gate.verify_acceptance') as historical:
            with self.assertRaisesRegex(gate.Rejected, 'exact project owner authorization'):
                verify(self.repair, self.fixture.plan, self.fixture.accepted, self.api, self.grant, False)
            self.fixture.comments = [{'user': {'login': OWNER},
                                      'body': 'GENESIS-OWNER-APPROVED: ' + self.repair['head']['sha']}]
            for check in self.fixture.runs:
                check['head_sha'] = self.repair['head']['sha']
            state = copy.deepcopy((self.fixture.plan, self.fixture.accepted))
            self.assertIn('F00-V0', verify(self.repair, self.fixture.plan, self.fixture.accepted,
                                           self.api, self.grant, True))
            self.assertTrue(any(call.args[1]['pr'] == 45 for call in historical.call_args_list))
            self.assertEqual(state, (self.fixture.plan, self.fixture.accepted))

    def test_migration_requires_actual_exact_repair_merge_on_bootstrapped_base(self):
        migration = self.migration
        self.assertEqual(BRANCH, migration['head']['ref'])
        hotfix = migration['base']['sha']
        merged = REPAIR_MERGE
        repair = self.repair
        responses = {'/pulls/48': repair, f'/git/commits/{merged}': {'parents': [
            {'sha': BOOTSTRAP}, {'sha': repair['head']['sha']}]},
            f'/git/commits/{BOOTSTRAP}': {'parents': [{'sha': self.grant['prior_bootstrap']}]},
            f"/git/commits/{self.grant['prior_bootstrap']}": {'parents': [{'sha': INITIAL_BOOTSTRAP}]},
            f'/git/commits/{INITIAL_BOOTSTRAP}': {'parents': [{'sha': self.grant['source_main']}]},

            f'/git/commits/{hotfix}': {'parents': [{'sha': merged}]},
            f'/compare/{merged}...{hotfix}': {'status': 'ahead', 'ahead_by': 1,
                                           'merge_base_commit': {'sha': merged},
                                           'files': [{'filename': f, 'status': 'modified'} for f in HOTFIX_PATHS]},
            '/issues/1': {'state': 'open'}}
        self.fixture.comments.append({'user': {'login': OWNER},
                                      'body': 'GENESIS-OWNER-APPROVED: ' + repair['head']['sha']})
        with patch.object(self.api, 'call', side_effect=responses.__getitem__):
            with self.assertRaisesRegex(gate.Rejected, 'approved and merged'):
                verify(migration, self.fixture.plan, self.fixture.accepted, self.api, self.grant, False)
            repair.update(merged=True, merge_commit_sha=merged, merged_at='2026-11-04T12:00:00Z')
            with self.assertRaisesRegex(gate.Rejected, 'authenticated approval'):
                verify(migration, self.fixture.plan, self.fixture.accepted, self.api, self.grant, False)
            self.fixture.comments.append({'user': {'login': OWNER}, 'body': hotfix_marker(merged, hotfix)})
            pilot = next(run for run in self.fixture.runs if run['name'] == 'pilot-checks')
            self.fixture.runs.append(dict(pilot, head_sha=merged))
            before = copy.deepcopy((self.fixture.plan, self.fixture.accepted, self.migration, self.grant))
            with patch.object(CandidateChecks, 'wait') as wait:
                self.assertIn('F01-GOV', verify(migration, self.fixture.plan, self.fixture.accepted,
                                                self.api, self.grant, True))
                wait.assert_called_once()
            self.assertEqual(before, (self.fixture.plan, self.fixture.accepted, self.migration, self.grant))
            responses[f'/git/commits/{hotfix}']['parents'] = [{'sha': '2' * 40}]
            with self.assertRaisesRegex(gate.Rejected, 'one protected hotfix'):
                verify(migration, self.fixture.plan, self.fixture.accepted, self.api, self.grant, False)
            responses[f'/git/commits/{hotfix}']['parents'] = [{'sha': merged}]
            responses[f'/git/commits/{merged}']['parents'][1]['sha'] = 'e' * 40
            with self.assertRaisesRegex(gate.Rejected, 'merge parents differ'):
                verify(migration, self.fixture.plan, self.fixture.accepted, self.api, self.grant, True)


def log_for(sha, *, second_fetch=False, fake_after=False):
    command = f'[command]/usr/bin/git -c protocol.version=2 fetch --depth=1 origin +{sha}:refs/remotes/pull/49/merge'
    lines = [f'##[group]Run {CHECKOUT}', '##[endgroup]', command]
    if second_fetch:
        lines.append(command)
    lines.extend(('[command]/usr/bin/git log -1 --format=%H', sha, '##[group]Run python3 tests.py'))
    if fake_after:
        lines.extend((command, '[command]/usr/bin/git log -1 --format=%H', 'f' * 40))
    return '\n'.join('2026-11-04T15:00:00Z ' + line for line in lines)


class CandidateEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.head, self.base, self.tree = 'a' * 40, 'b' * 40, 'c' * 40
        self.checkout, self.old, self.pr_preview = 'd' * 40, 'e' * 40, 'f' * 40
        self.name = 'pilot-checks'
        self.api = unittest.mock.Mock()
        self.pr = {'number': 49, 'head': {'sha': self.head}, 'base': {'sha': self.base},
                   'merge_commit_sha': self.pr_preview}
        self.routes = {}
        self.logs = {}
        self.api.call.side_effect = self.routes.__getitem__
        self.checker = CandidateChecks(self.api, self.pr, read_log=self.logs.__getitem__)
        self.commit(self.pr_preview, self.base)
        self.commit(self.checkout, self.base)
        self.commit(self.old, '0' * 40)

    def commit(self, checkout, base):
        self.routes[f'/git/commits/{checkout}'] = dict(
            sha=checkout, parents=[{'sha': base}, {'sha': self.head}], tree={'sha': self.tree})

    def candidate_run(self, number, checkout=None, result='success', *, status='completed', app=15368, name=None):
        name = name or self.name
        workflow, blob = WORKFLOWS[name]
        record = dict(id=number, name=name, head_sha=self.head, status=status, conclusion=result,
                      app={'id': app, 'slug': 'github-actions'}, check_suite={'id': number},
                      started_at=f'2026-11-04T15:00:{number:02d}Z')
        self.routes[f'/actions/jobs/{number}'] = dict(
            id=number, name=name, run_id=number, run_attempt=1, head_sha=self.head, status=status,
            conclusion=result, check_run_url=f'https://api.github.com/repos/{REPO}/check-runs/{number}',
            steps=[{'number': 1, 'name': 'Set up job'},
                   {'number': 2, 'name': f'Run {CHECKOUT}', 'conclusion': 'success'}])
        self.routes[f'/actions/runs/{number}/attempts/1'] = dict(
            id=number, run_attempt=1, event='pull_request', path=workflow, head_sha=self.head,
            repository={'full_name': REPO}, head_repository={'full_name': REPO}, check_suite_id=number,
            pull_requests=[{'number': 49, 'base': {'sha': self.base}}])
        for revision in {self.head, self.base, checkout}:
            self.routes[f'/contents/{workflow}?ref={revision}'] = {'type': 'file', 'sha': blob}
        if checkout:
            self.logs[number] = log_for(checkout)
        return record

    def test_obsolete_checkout_with_current_api_base_is_wrong_base(self):
        current = self.candidate_run(1, self.checkout)
        obsolete = self.candidate_run(2, self.old, 'failure')
        self.assertEqual('WRONG_BASE', self.checker.state([obsolete], self.name, self.tree))
        self.assertEqual('PASSED', self.checker.state([current, obsolete], self.name, self.tree))
        calls = self.api.call.call_count
        self.assertEqual('PASSED', self.checker.state([obsolete, current], self.name, self.tree))
        self.assertEqual(calls, self.api.call.call_count)

    def test_latest_relevant_failure_supersedes_success(self):
        old = self.candidate_run(1, self.checkout)
        later = self.candidate_run(2, self.checkout, 'failure')
        self.assertEqual('FAILED', self.checker.state([old, later], self.name, self.tree))

    def test_provenance_is_limited_to_pinned_checkout_step(self):
        self.assertEqual(self.checkout, checkout_sha(log_for(self.checkout, fake_after=True), 49))
        for log in ('', log_for(self.checkout, second_fetch=True),
                    log_for(self.checkout).replace('##[group]Run actions/checkout', '##[group]Run echo'),
                    log_for(self.checkout).replace('/pull/49/merge', '/pull/48/merge')):
            with self.subTest(log=log):
                with self.assertRaisesRegex(gate.Rejected, 'provenance'):
                    checkout_sha(log, 49)

    def test_wrong_head_parent_or_candidate_tree_fails_closed(self):
        record = self.candidate_run(1, self.checkout)
        self.routes[f'/git/commits/{self.checkout}']['parents'][1]['sha'] = '0' * 40
        with self.assertRaisesRegex(gate.Rejected, 'merge parents'):
            self.checker.state([record], self.name, self.tree)
        self.commit(self.checkout, self.base)
        self.routes[f'/git/commits/{self.checkout}']['tree']['sha'] = '0' * 40
        with self.assertRaisesRegex(gate.Rejected, 'merge tree differs'):
            self.checker.state([record], self.name, self.tree)

    def test_wrong_app_or_forged_actions_metadata_is_rejected(self):
        self.assertEqual('MISSING', self.checker.state([self.candidate_run(1, self.checkout, app=99)], self.name, self.tree))
        forged = self.candidate_run(2, self.checkout)
        self.routes['/actions/runs/2/attempts/1']['event'] = 'workflow_dispatch'
        with self.assertRaisesRegex(gate.Rejected, 'job provenance mismatch'):
            self.checker.state([forged], self.name, self.tree)

    def test_unreviewed_workflow_cannot_supply_checkout_logs(self):
        record = self.candidate_run(1, self.checkout)
        workflow = WORKFLOWS[self.name][0]
        self.routes[f'/contents/{workflow}?ref={self.head}']['sha'] = '0' * 40
        self.checker.read_log = unittest.mock.Mock()
        with self.assertRaisesRegex(gate.Rejected, 'Unverified workflow definition'):
            self.checker.state([record], self.name, self.tree)
        self.checker.read_log.assert_not_called()

    def wait_for(self, states, *, timeout=5, names=('governance-tests',)):
        path = f'/commits/{self.head}/check-runs?filter=latest&per_page=100'
        polls = iter(states)
        elapsed = [0]
        def call(path_requested):
            if path_requested == path:
                rows = next(polls)
                return {'total_count': len(rows), 'check_runs': rows}
            return self.routes[path_requested]
        def pause(seconds):
            elapsed[0] += seconds
        self.api.call.side_effect = call
        self.checker.wait(names, timeout=timeout, clock=lambda: elapsed[0], pause=pause)
        return elapsed[0]

    def test_pending_governance_can_finish_successfully(self):
        pending = self.candidate_run(1, status='in_progress', name='governance-tests')
        complete = self.candidate_run(2, self.checkout, name='governance-tests')
        self.assertEqual(5, self.wait_for([[pending], [complete]]))

    def test_pending_governance_can_finish_with_failure(self):
        pending = self.candidate_run(1, status='in_progress', name='governance-tests')
        failed = self.candidate_run(2, self.checkout, 'failure', name='governance-tests')
        with self.assertRaisesRegex(gate.Rejected, 'current required candidate check failed'):
            self.wait_for([[pending], [failed]])

    def test_current_failure_waits_for_other_mandatory_check_to_settle(self):
        failed = self.candidate_run(1, self.checkout, 'failure', name='governance-tests')
        pending = self.candidate_run(2, status='in_progress')
        complete = self.candidate_run(3, self.checkout)
        with self.assertRaisesRegex(gate.Rejected, 'current required candidate check failed'):
            self.wait_for([[failed, pending], [failed, complete]],
                          names=('governance-tests', 'pilot-checks'))
        self.assertIn(3, self.checker.proven)

    def test_wrong_head_is_stale_even_with_a_trusted_app(self):
        check = self.candidate_run(1, self.checkout)
        check['head_sha'] = '0' * 40
        self.assertEqual('STALE', self.checker.state([check], self.name, self.tree))

    def test_missing_and_perpetually_pending_checks_time_out(self):
        pending = self.candidate_run(1, status='queued', name='governance-tests')
        for rows, status in (([], 'MISSING'), ([pending], 'PENDING')):
            with self.subTest(status=status):
                with self.assertRaisesRegex(gate.Rejected, 'Timed out.*' + status):
                    self.wait_for([rows, rows])

    def test_hotfix_grant_rejects_extra_paths_and_wrong_actor(self):
        files = [dict(filename=f, status='modified') for f in HOTFIX_PATHS]
        self.routes.update({f'/git/commits/{self.checkout}': {'parents': [{'sha': self.base}]},
                            f'/compare/{self.base}...{self.checkout}':
                            {'status': 'ahead', 'ahead_by': 1, 'merge_base_commit': {'sha': self.base}, 'files': files}})
        comment = {'body': hotfix_marker(self.base, self.checkout), 'user': {'login': 'other'}}
        with self.assertRaisesRegex(gate.Rejected, 'authenticated approval'):
            verify_hotfix(self.api, self.base, self.checkout, [comment])
        comment['user']['login'] = OWNER
        verify_hotfix(self.api, self.base, self.checkout, [comment])
        files.append(dict(filename='.github/acceptance.json', status='modified'))
        with self.assertRaisesRegex(gate.Rejected, 'exact protected path scope'):
            verify_hotfix(self.api, self.base, self.checkout, [comment])


if __name__ == '__main__':
    unittest.main()
