"""Recovery sequencing tests for the separately approved historical repair."""
import copy
import unittest
from unittest.mock import patch

import test_v3_activation as original
from v3_activation import BRANCH, OWNER, REPAIR_BRANCH, verify
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
        merged = migration['base']['sha']
        repair = self.repair
        responses = {'/pulls/48': repair, f'/git/commits/{merged}': {'parents': [
            {'sha': 'b' * 40}, {'sha': repair['head']['sha']}]},
            f"/git/commits/{'b' * 40}": {'parents': [{'sha': self.grant['prior_bootstrap']}]},
            '/issues/1': {'state': 'open'}}
        self.fixture.comments.append({'user': {'login': OWNER},
                                      'body': 'GENESIS-OWNER-APPROVED: ' + repair['head']['sha']})
        with patch.object(self.api, 'call', side_effect=responses.__getitem__):
            with self.assertRaisesRegex(gate.Rejected, 'approved and merged'):
                verify(migration, self.fixture.plan, self.fixture.accepted, self.api, self.grant, False)
            repair.update(merged=True, merge_commit_sha=merged, merged_at='2026-11-04T12:00:00Z')
            pilot = next(run for run in self.fixture.runs if run['name'] == 'pilot-checks')
            self.fixture.runs.append(dict(pilot, head_sha=merged))
            with self.assertRaisesRegex(gate.Rejected, 'pilot-checks'):
                verify(migration, self.fixture.plan, self.fixture.accepted, self.api, self.grant, True)
            pilot['started_at'] = '2026-11-04T12:01:00Z'
            self.assertIn('F01-GOV', verify(migration, self.fixture.plan, self.fixture.accepted,
                                            self.api, self.grant, True))
            responses[f'/git/commits/{merged}']['parents'][1]['sha'] = 'e' * 40
            with self.assertRaisesRegex(gate.Rejected, 'merge parents differ'):
                verify(migration, self.fixture.plan, self.fixture.accepted, self.api, self.grant, True)


if __name__ == '__main__':
    unittest.main()
