"""Regression cases for the 23 October operational audit; no live writes."""
import copy
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from test_gate import API, PLAN
from gate import (Rejected, evaluate, readiness, validate_plan, verify_acceptance,
                  required_checks, same_revision, successful_checks, owner_approval)
from security_check import file_errors
from sync_issues import synchronize

class AuditGateTests(unittest.TestCase):
    def setUp(self):
        self.plan = copy.deepcopy(PLAN)
        self.api = API()
        self.api.issue = {'state': 'open'}
        self.task = self.plan['tasks'][0]

    def ready(self):
        return readiness(self.api.pr, self.plan, {}, self.api)

    def test_current_pr_without_owner_approval_fails_readiness(self):
        self.api.comments = []
        self.assertIn('all 0', evaluate(self.api.pr, self.plan, {}, self.api))
        with self.assertRaisesRegex(Rejected, 'current Burkay'):
            self.ready()

    def test_owner_approval_and_real_checks_pass(self):
        self.assertIn('applicable CI verified', self.ready())

    def test_owner_can_approve_own_pr(self):
        self.api.pr['user']['login'] = 'cakarburkayy'
        self.assertIn('applicable CI verified', self.ready())

    def test_owner_author_commit_does_not_invalidate_owner_approval(self):
        self.api.commits.append({'author': {'login': 'cakarburkayy'}})
        self.assertIn('applicable CI verified', self.ready())

    def test_other_developer_cannot_issue_owner_approval(self):
        self.api.comments[0]['user']['login'] = 'ismail-cevik'
        with self.assertRaisesRegex(Rejected, 'current Burkay'):
            self.ready()

    def test_unlinked_commit_identity_does_not_crash(self):
        self.api.commits.append({'author': None, 'committer': None})
        self.assertIn('applicable CI verified', self.ready())

    def test_current_pr_failed_ci_blocks(self):
        self.api.checks[0]['conclusion'] = 'failure'
        with self.assertRaisesRegex(Rejected, 'Missing/failed'):
            self.ready()

    def test_current_pr_missing_ci_blocks(self):
        self.api.checks = []
        with self.assertRaisesRegex(Rejected, 'Missing/failed'):
            self.ready()

    def test_current_pr_skipped_ci_blocks(self):
        self.api.checks[0]['conclusion'] = 'skipped'
        with self.assertRaisesRegex(Rejected, 'Missing/failed'):
            self.ready()

    def test_draft_pr_blocks_readiness(self):
        self.api.pr['draft'] = True
        with self.assertRaisesRegex(Rejected, 'open and ready'):
            self.ready()

    def test_outsider_cannot_claim_registered_task(self):
        self.api.pr['user']['login'] = 'unregistered-person'
        with self.assertRaisesRegex(Rejected, 'authorized active developer'):
            evaluate(self.api.pr, self.plan, {}, self.api)

    def test_other_team_member_cannot_steal_current_task(self):
        self.api.pr['user']['login'] = 'caferkilinc'
        with self.assertRaisesRegex(Rejected, 'authorized active developer'):
            self.ready()

    def test_wrong_base_rejected(self):
        self.api.pr['base']['ref'] = 'other'
        with self.assertRaisesRegex(Rejected, 'Wrong integration'):
            self.ready()

    def test_truncated_file_list_fails_closed(self):
        self.api.pr['changed_files'] = 2
        with self.assertRaisesRegex(Rejected, 'Incomplete changed-file'):
            self.ready()

    def test_rename_checks_both_paths(self):
        self.api.files[0]['previous_filename'] = 'backend/private.py'
        with self.assertRaisesRegex(Rejected, 'Out-of-task path'):
            self.ready()

    def test_mismatched_dependency_numbers_rejected(self):
        self.plan['tasks'][1]['dependency_issues'] = []
        with self.assertRaisesRegex(Rejected, 'native issue prerequisites'):
            validate_plan(self.plan)

    def test_unknown_team_member_rejected(self):
        self.plan['sequential_execution']['team_sequence'][2] = 'unknown'
        with self.assertRaisesRegex(Rejected, 'rotation'):
            validate_plan(self.plan)

    def test_invalid_calendar_date_rejected(self):
        self.task['start'] = '2026-02-30'
        with self.assertRaises(ValueError):
            validate_plan(self.plan)

    def test_nan_effort_rejected(self):
        self.task['estimated_effort'] = float('nan')
        with self.assertRaisesRegex(Rejected, 'Invalid estimate'):
            validate_plan(self.plan)

    def test_wrong_parent_rejected(self):
        self.task['parent_issue'] = 7
        with self.assertRaisesRegex(Rejected, 'Wrong parent'):
            validate_plan(self.plan)

    def test_duplicate_prerequisite_rejected(self):
        self.plan['tasks'][1]['dependencies'] *= 2
        with self.assertRaisesRegex(Rejected, 'Duplicate prerequisite'):
            validate_plan(self.plan)

    def test_peer_changes_request_is_not_a_required_approval(self):
        self.api.reviews = [{'user': {'login': 'tahaugurtoyran'}, 'state': 'CHANGES_REQUESTED'}]
        self.assertIn('applicable CI verified', self.ready())

    def test_missing_exact_sha_blocks(self):
        self.api.comments[0]['body'] = 'GENESIS-OWNER-APPROVED: prior-sha'
        with self.assertRaisesRegex(Rejected, 'current Burkay'):
            self.ready()

    def test_case_insensitive_owner_login(self):
        self.api.comments[0]['user']['login'] = 'CAKARBURKAYY'
        self.assertIn('applicable CI verified', self.ready())

    def test_no_approval_from_read_only_peer(self):
        self.api.comments = [{'user': {'login': 'caferkilinc'}, 'body': 'GENESIS-OWNER-APPROVED: abc'}]
        with self.assertRaisesRegex(Rejected, 'current Burkay'):
            self.ready()

    def test_task_modules_require_both_checks(self):
        for number in (10, 22, 30, 31, 34, 35):
            t = next(t for t in self.plan['tasks'] if t['issue_number'] == number)
            self.assertTrue({'backend-checks', 'frontend-checks'} <= set(t['required_checks']))

    def test_actual_backend_path_adds_check_even_on_frontend_task(self):
        t = next(t for t in self.plan['tasks'] if t['issue_number'] == 21)
        self.assertIn('backend-checks', required_checks(t, [{'filename': 'backend/api/app.py'}]))

    def test_schemas_require_contract_check(self):
        self.assertIn('contract-checks', required_checks(self.task, [{'filename': 'backend/core/schemas/types.py'}]))

    def test_pilot_requires_actual_java_pilot_check(self):
        t = next(t for t in self.plan['tasks'] if t['issue_number'] == 9)
        self.assertIn('pilot-checks', t['required_checks'])
        self.assertIn('.github/workflows/pilot-checks.yml', t['allowed_paths'])

    def test_old_policy_sha_rejected(self):
        with self.assertRaisesRegex(Rejected, 'Trusted main moved'):
            same_revision(self.api.pr, 'abc', 'old-base')

    def test_current_main_policy_sha_passes(self):
        same_revision(self.api.pr, 'abc', 'base')

    def test_old_head_event_rejected(self):
        with self.assertRaisesRegex(Rejected, 'PR head moved'):
            same_revision(self.api.pr, 'old-head', 'base')

    def test_string_evidence_rejected(self):
        self.api.issue = {'state': 'closed', 'state_reason': 'completed'}
        with self.assertRaisesRegex(Rejected, 'Missing HTTPS evidence'):
            verify_acceptance(self.task, {'pr': 101, 'head_sha': 'abc', 'evidence': 'https://example.org'}, self.api, self.plan)

    def test_boolean_pr_number_rejected(self):
        self.api.issue = {'state': 'closed', 'state_reason': 'completed'}
        with self.assertRaisesRegex(Rejected, 'acceptance PR number'):
            verify_acceptance(self.task, {'pr': True, 'head_sha': 'abc', 'evidence': ['https://example.org']}, self.api, self.plan)

    def test_credentials_in_evidence_url_rejected(self):
        with self.assertRaisesRegex(Rejected, 'Missing HTTPS evidence'):
            verify_acceptance(self.task, {'pr': 101, 'evidence': ['https://u:p@example.org']}, self.api, self.plan)

    def test_unrelated_ci_commit_cannot_be_used(self):
        with self.assertRaisesRegex(Rejected, 'unrelated'):
            successful_checks(self.task, self.api.pr, self.api.files, self.api, 'unrelated-sha')

    def test_accepted_pr_merge_revision_can_be_used(self):
        self.api.pr['merge_commit_sha'] = 'merge-sha'
        successful_checks(self.task, self.api.pr, self.api.files, self.api, 'merge-sha')

class HygieneTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def check_file(self, name, content=b'ordinary text'):
        p = self.root / name; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(content)
        return file_errors(self.root, name)

    def test_nested_upload_blocked(self):
        self.assertTrue(self.check_file('backend/uploads/user-code.txt'))

    def test_nested_private_blocked(self):
        self.assertTrue(self.check_file('backend/PRIVATE/notes.txt'))

    def test_nested_environment_blocked(self):
        self.assertTrue(self.check_file('backend/.env.local'))

    def test_placeholder_environment_example_allowed(self):
        self.assertEqual([], self.check_file('backend/.env.example', b'KEY=placeholder'))

    def test_invalid_utf8_does_not_hide_ascii_key(self):
        value = ('gh' + 'p_' + 'a' * 36).encode()
        self.assertTrue(self.check_file('bad-encoding.txt', b'\xff' + value))

    def test_provider_project_key_detected(self):
        value = ('sk-' + 'proj-' + 'a' * 30).encode()
        self.assertTrue(self.check_file('config.txt', value))

    def test_file_link_not_followed(self):
        self.check_file('target.txt');(self.root / 'link.txt').symlink_to('target.txt')
        self.assertIn('Symlink', file_errors(self.root, 'link.txt')[0])

    def test_directory_link_not_followed(self):
        self.check_file('real/target.txt');(self.root / 'linked').symlink_to('real', target_is_directory=True)
        self.assertIn('Symlink', file_errors(self.root, 'linked/target.txt')[0])

class SyncTests(unittest.TestCase):
    class FakeGraph:
        def __init__(self, bad=False, bad_marker=False):
            self.writes=[];self.bad=bad;self.bad_marker=bad_marker
        def call(self, path, method='GET', data=None, **kw):
            if method != 'GET': self.writes.append((path,data)); return {}
            if path.startswith('/labels/'): return {}
            n = int(path.split('/')[2])
            if path.endswith('/parent'):
                if self.bad and n == PLAN['tasks'][-1]['issue_number']: return {'number': 999}
                return None
            task = next((t for t in PLAN['tasks'] if t['issue_number'] == n), None)
            body = f"<!-- plan-id: {task['plan_id']} -->" if task else ""
            if task and n == 42 and self.bad_marker:
                body = "<!-- plan-id: MALICIOUS -->"
            return {'id': n, 'body': body}
        def pages(self, path, **kw): return []

    def test_late_graph_conflict_causes_no_earlier_writes(self):
        api=self.FakeGraph(bad=True)
        with self.assertRaisesRegex(RuntimeError,'Unexpected parent'):
            synchronize(PLAN,api)
        self.assertEqual([],api.writes)

    def test_wrong_live_task_identity_aborts_before_first_write(self):
        api=self.FakeGraph(bad_marker=True)
        with self.assertRaisesRegex(RuntimeError, 'Unexpected Plan ID marker'):
            synchronize(PLAN,api)
        self.assertEqual([],api.writes)

    def test_valid_preflight_then_only_expected_additions(self):
        api=self.FakeGraph()
        with redirect_stdout(io.StringIO()): synchronize(PLAN,api)
        self.assertEqual(len(PLAN['tasks']) + sum(len(t['dependencies']) for t in PLAN['tasks']),len(api.writes))


class LivePlanAuditTests(unittest.TestCase):
    class Fake:
        def __init__(self):
            self.issues={}
            self.dependencies={}
            for t in PLAN['tasks']:
                body='\n'.join([f"<!-- plan-id: {t['plan_id']} -->"]+[f'- {key}: {value}' for key,value in (
                    ('Priority',t['priority']),('Planned Start',t['start']),
                    ('Target Date',t['target']))]+[
                    f"- Estimated Effort: {t['effort_min']}–{t['effort_max']} person-hours; midpoint {t['estimated_effort']}."])
                self.issues[t['issue_number']]={'number':t['issue_number'],'assignees':[],'body':body}
                self.dependencies[t['issue_number']]=[{'number':n} for n in t['dependency_issues']]
        def pages(self,path,**kw):
            n=int(path.split('/')[2])
            if path.endswith('/sub_issues'):
                return [self.issues[t['issue_number']] for t in PLAN['tasks'] if t['parent_issue']==n]
            return self.dependencies[n]
    def test_consistent_plan_has_no_errors(self):
        from audit_plan import audit
        self.assertEqual([],audit(PLAN,self.Fake()))
    def test_completed_migration_rejects_static_assignees(self):
        from audit_plan import audit
        p=copy.deepcopy(PLAN);p['assignment_migration']['status']='COMPLETE'
        a=self.Fake();a.issues[8]['assignees']=[{'login':'caferkilinc'}]
        self.assertIn('#8: unexpected fixed assignee',audit(p,a))
    def test_dependency_drift_is_reported(self):
        from audit_plan import audit
        a=self.Fake();a.dependencies[9]=[]
        self.assertIn('#9: native prerequisite drift',audit(PLAN,a))
    def test_date_drift_is_reported(self):
        from audit_plan import audit
        a=self.Fake();a.issues[8]['body']=a.issues[8]['body'].replace('2026-10-25','2026-10-24')
        self.assertIn('#8: issue body no longer matches plan',audit(PLAN,a))

class PolicyBoundaryTests(unittest.TestCase):
    def test_application_task_cannot_replace_governance_tests(self):
        from gate import check_paths
        t=next(t for t in PLAN['tasks'] if t['issue_number']==12)
        with self.assertRaisesRegex(Rejected,'Governance policy changes'):
            check_paths(t,[{'filename':'tests/governance/test_gate.py'}])
    def test_environment_task_cannot_replace_dependency_workflow(self):
        from gate import check_paths
        t=next(t for t in PLAN['tasks'] if t['issue_number']==10)
        with self.assertRaisesRegex(Rejected,'Governance policy changes'):
            check_paths(t,[{'filename':'.github/workflows/dependency-gate.yml'}])
    def test_environment_task_can_create_real_application_ci(self):
        from gate import check_paths
        t=next(t for t in PLAN['tasks'] if t['issue_number']==10)
        check_paths(t,[{'filename':'.github/workflows/application-ci.yml'}])

if __name__ == '__main__':
    unittest.main()
