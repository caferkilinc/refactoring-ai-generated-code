"""Temporary trusted-main gate for one owner-authorized Genesis v3 activation."""
import argparse
import json
import os
import re
import time
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener
from pathlib import Path

import gate

ROOT = Path(__file__).resolve().parents[2]
REPAIR_BRANCH = 'fix/9-pilot-integrity-and-status'
BRANCH = 'chore/1-genesis-v3-phase1'
REPO = 'caferkilinc/refactoring-ai-generated-code'
OWNER = 'cakarburkayy'
V3 = ROOT / 'docs/governance/PROJECT_GENESIS_CODEX_NATIVE_PROTOCOL_V3.md'


REPAIR_MERGE = '07e5ac33e3040b14cdad078d24b85deb281e0e83'
BOOTSTRAP = '45cc7dd0a67752f92614d0112ccbb65e8b45db11'
INITIAL_BOOTSTRAP = 'c8d820e2d52485954873cda8f09f0c0ba0413678'
APPROVED_HOTFIX = '9e5a248743bfaae29896c640991f3608aca3d3e7'
API_COMPAT_PATHS = {
    'scripts/governance/github_api.py',
    'scripts/governance/v3_activation.py',
    'tests/governance/test_v3_recovery.py',
}
HOTFIX_PATHS = {
    '.github/workflows/dependency-gate.yml',
    'scripts/governance/v3_activation.py',
    'tests/governance/test_v3_recovery.py',
}
CHECKOUT = 'actions/checkout@d23441a48e516b6c34aea4fa41551a30e30af803'
WORKFLOWS = {
    'pilot-checks': ('.github/workflows/pilot-checks.yml', '84bd32de68923ee29c21778b020e2ce3e140f9ce'),
    **{name: ('.github/workflows/governance-ci.yml', '4a9a8957314f1f0bf1a49301136f05418dd9b68f')
       for name in ('governance-tests', 'documentation-checks', 'security-checks')},
}


def hotfix_marker(repair, revision):
    return f'GENESIS-HOTFIX-APPROVED: {REPO} #49 {repair} {revision}'


def compatibility_marker(revision):
    return f'GENESIS-API-COMPAT-APPROVED: {REPO} #49 {APPROVED_HOTFIX} {revision}'


def verify_protected_revision(api, parent, revision, paths, comments, marker, label):
    gate.require(revision != parent and parents(api, revision) == [parent],
                 f'Expected one protected {label} immediately after {parent}')
    comparison = api.call(f'/compare/{parent}...{revision}')
    files = comparison.get('files') or []
    gate.require(comparison['status'] == 'ahead' and comparison['ahead_by'] == 1
                 and (comparison.get('merge_base_commit') or {}).get('sha') == parent
                 and len(files) == len(paths) and {f['filename'] for f in files} == paths
                 and all(f['status'] == 'modified' and not f.get('previous_filename') for f in files),
                 f'{label} revision exceeds the exact protected path scope')
    gate.require(owner_marker(comments, marker),
                 f'Missing authenticated approval for this exact trusted {label} revision')


def verify_hotfix(api, repair, revision, comments):
    verify_protected_revision(api, repair, revision, HOTFIX_PATHS, comments,
                              hotfix_marker(repair, revision), 'hotfix')


def verify_compatibility(api, revision, comments):
    verify_protected_revision(api, APPROVED_HOTFIX, revision, API_COMPAT_PATHS, comments,
                              compatibility_marker(revision), 'API compatibility fix')


def owner_marker(comments, marker):
    return any((c.get('user') or {}).get('login', '').casefold() == OWNER
               and (c.get('body') or '').strip() == marker for c in comments)


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, url):
        return None


def job_logs(job_id):
    """Read GitHub's first-party job log without forwarding credentials to storage."""
    opener = build_opener(NoRedirect())
    request = Request(f'https://api.github.com/repos/{REPO}/actions/jobs/{job_id}/logs',
                      headers={'Authorization': 'Bearer ' + os.environ['GH_TOKEN'],
                               'Accept': 'application/vnd.github+json',
                               'X-GitHub-Api-Version': '2022-11-28'})
    try:
        with opener.open(request, timeout=10) as response:
            data = response.read(4 * 1024 * 1024 + 1)
    except HTTPError as exc:
        location = urlsplit(exc.headers.get('Location', ''))
        gate.require(exc.code == 302 and location.scheme == 'https'
                     and (location.hostname or '').endswith('.blob.core.windows.net')
                     and not location.username and not location.password and location.port is None,
                     f'Job log unavailable from GitHub Actions: {job_id} (HTTP {exc.code})')
        try:
            with opener.open(location.geturl(), timeout=10) as response:
                data = response.read(4 * 1024 * 1024 + 1)
        except OSError:
            raise gate.Rejected(f'GitHub Actions log download failed for job {job_id}') from None
    gate.require(len(data) <= 4 * 1024 * 1024, f'GitHub Actions log exceeds limit: {job_id}')
    return data.decode('utf-8', errors='replace')


def checkout_sha(log, number):
    # Workflow and checkout action are pinned, and checkout precedes all candidate code.
    lines = [line.split(' ', 1)[1] for line in log.splitlines()
             if re.match(r'^\d{4}-\d\d-\d\dT[^ ]+Z ', line)]
    starts = [i for i, line in enumerate(lines) if line.startswith('##[group]Run ')]
    gate.require(len(starts) >= 2 and lines[starts[0]] == f'##[group]Run {CHECKOUT}',
                 'Checkout provenance missing or not the first workflow step')
    segment = lines[starts[0] + 1:starts[1]]
    fetch = [m[1] for line in segment if (m := re.fullmatch(
        rf'\[command\]/usr/bin/git .* fetch .* \+([a-f0-9]{{40}}):refs/remotes/pull/{number}/merge', line))]
    reports = [segment[i + 1] for i, line in enumerate(segment[:-1])
               if line == '[command]/usr/bin/git log -1 --format=%H']
    gate.require(len(fetch) == 1 and reports == fetch, 'Checkout provenance missing or ambiguous')
    return fetch[0]


class CandidateChecks:
    def __init__(self, api, pr, *, read_log=job_logs):
        self.api, self.pr, self.read_log = api, pr, read_log
        self.head, self.base = pr['head']['sha'], pr['base']['sha']
        self.proven = {}
        self.workflow_blobs = set()

    def evidence(self, check, name, expected_tree):
        job_id = check['id']
        if job_id in self.proven:
            return self.proven[job_id]
        job = self.api.call(f'/actions/jobs/{job_id}')
        workflow, blob = WORKFLOWS[name]
        run = self.api.call(f"/actions/runs/{job['run_id']}/attempts/{job['run_attempt']}")
        gate.require(job['id'] == job_id and job['name'] == name
                     and job['head_sha'] == self.head and job['status'] == 'completed'
                     and job['conclusion'] == check['conclusion']
                     and job['check_run_url'] == f'https://api.github.com/repos/{REPO}/check-runs/{job_id}'
                     and run['id'] == job['run_id'] and run['run_attempt'] == job['run_attempt']
                     and run['check_suite_id'] == check['check_suite']['id']
                     and run['event'] == 'pull_request' and run['path'] == workflow
                     and run['head_sha'] == self.head and run['repository']['full_name'] == REPO
                     and run['head_repository']['full_name'] == REPO
                     and {p['number'] for p in run['pull_requests']} == {self.pr['number']},
                     f'Actions job provenance mismatch: {job_id}')
        steps = sorted(job['steps'], key=lambda step: step['number'])
        gate.require(len(steps) > 1 and steps[0]['name'] == 'Set up job'
                     and steps[1]['name'] == f'Run {CHECKOUT}' and steps[1]['conclusion'] == 'success',
                     f'Pinned checkout step unavailable: {job_id}')
        # Establish the workflow definition independently before interpreting checkout output.
        self.verify_workflow(workflow, blob, self.head)
        self.verify_workflow(workflow, blob, self.base)
        checkout = checkout_sha(self.read_log(job_id), self.pr['number'])
        commit = self.api.call(f'/git/commits/{checkout}')
        self.verify_workflow(workflow, blob, checkout)
        sources = [p['sha'] for p in commit['parents']]
        gate.require(commit['sha'] == checkout and len(sources) == 2 and sources[1] == self.head,
                     f'Unexpected tested merge parents: {checkout}')
        if sources[0] != self.base:
            result = 'WRONG_BASE'
        else:
            gate.require(commit['tree']['sha'] == expected_tree,
                         f'Tested merge tree differs from the current PR candidate: {checkout}')
            result = 'PASSED' if check['conclusion'] == 'success' else 'FAILED'
        self.proven[job_id] = result
        print(f'{name} job {job_id}, checkout {checkout}: {result}', flush=True)
        return result

    def verify_workflow(self, path, blob, revision):
        key = path, revision
        if key not in self.workflow_blobs:
            info = self.api.call(f'/contents/{path}?ref={revision}')
            gate.require(info['type'] == 'file' and info['sha'] == blob,
                         f'Unverified workflow definition: {path} at {revision}')
            self.workflow_blobs.add(key)

    def state(self, runs, name, tree, *, deadline=None, clock=time.monotonic):
        official = [r for r in runs if r.get('name') == name
                    and (r.get('app') or {}).get('id') == 15368
                    and r['app'].get('slug') == 'github-actions']
        candidates = [r for r in official if r.get('head_sha') == self.head]
        # An undated queued result can be newer than any completed attempt.
        ordered = sorted(candidates, key=lambda r: (r.get('started_at') or '9999', r['id']), reverse=True)
        state = 'STALE' if official and not candidates else 'MISSING'
        for run in ordered:
            if run['status'] != 'completed':
                return 'PENDING'
            gate.require(deadline is None or clock() <= deadline,
                         f'Timed out verifying checkout evidence for {name}')
            state = self.evidence(run, name, tree)
            if state != 'WRONG_BASE':
                return state
        return state

    def wait(self, names, *, timeout=180, clock=time.monotonic, pause=time.sleep):
        gate.require(set(names) <= WORKFLOWS.keys(), 'Unsupported required candidate check')
        candidate = self.api.call(f"/git/commits/{self.pr['merge_commit_sha']}")
        gate.require([p['sha'] for p in candidate['parents']] == [self.base, self.head],
                     'Current PR merge preview does not use the verified base and head')
        tree = candidate['tree']['sha']
        deadline = clock() + timeout
        previous = None
        while True:
            payload = self.api.call(f'/commits/{self.head}/check-runs?filter=latest&per_page=100')
            gate.require(payload['total_count'] <= 100, 'Check run history exceeds bounded recovery scope')
            states = {name: self.state(payload['check_runs'], name, tree, deadline=deadline, clock=clock)
                      for name in sorted(names)}
            if states != previous:
                print(', '.join(f'{name}={state}' for name, state in states.items()), flush=True)
                previous = states
            if set(states.values()) <= {'PASSED', 'FAILED'}:
                gate.require(clock() <= deadline, 'Timed out verifying mandatory checkout evidence')
                gate.require('FAILED' not in states.values(), 'A current required candidate check failed')
                return
            remaining = deadline - clock()
            gate.require(remaining > 0, 'Timed out awaiting mandatory checks: ' + str(states))
            pause(min(5, remaining))


def parents(api, revision):
    return [parent['sha'] for parent in api.call(f'/git/commits/{revision}')['parents']]


def owner_decision(pr, api):
    marker = f"GENESIS-OWNER-APPROVED: {pr['head']['sha']}"
    return owner_marker(api.pages(f"/issues/{pr['number']}/comments"), marker)


def scope(pr, entry, branch):
    head, base = pr['head'], pr['base']
    gate.require(head['repo']['full_name'] == REPO and base['repo']['full_name'] == REPO
                 and base['ref'] == 'main', 'Wrong migration repository')
    gate.require(pr['number'] == entry['pr'] and head['ref'] == branch,
                 'Wrong migration task, PR or branch')
    gate.require(pr['user']['login'].casefold() == entry['author'].casefold(), 'Wrong migration author')
    gate.require(head['sha'] == entry['head'], 'Migration head is outside the trusted grant')


def verify(pr, plan, accepted, api, grant, readiness):
    need = gate.require
    head, base = pr['head'], pr['base']
    repair = grant.get('repair')
    repairing = pr['number'] == 48 and repair is not None
    task = gate.linked_task(pr, plan)
    entry, branch, issue_number, task_id = ((repair, REPAIR_BRANCH, 9, 'F00-V0') if repairing
                                          else (grant, BRANCH, 1, 'F01-GOV'))
    need(plan['repository'] == REPO and task['plan_id'] == task_id
         and task['issue_number'] == issue_number, 'Wrong migration repository or task')
    scope(pr, entry, branch)
    need(pr['state'] == 'open' and not pr.get('draft') and not pr.get('merged'), 'Migration PR is not ready')
    comments = api.pages(f"/issues/{pr['number']}/comments")
    expected_parent = grant.get('prior_bootstrap', grant['source_main'])
    if repair is not None and not repairing:
        repaired = api.call('/pulls/48')
        scope(repaired, repair, REPAIR_BRANCH)
        repair_sha = repaired.get('merge_commit_sha')
        need(repaired.get('merged') and repair_sha == REPAIR_MERGE and repaired.get('merged_at')
             and owner_decision(repaired, api), 'PR #48 must be approved and merged')
        merged_parents = parents(api, repair_sha)
        need(merged_parents == [BOOTSTRAP, repair['head']],
             'Pilot repair merge parents differ from the grant')
        need(parents(api, BOOTSTRAP) == [expected_parent]
             and parents(api, expected_parent) == [INITIAL_BOOTSTRAP]
             and parents(api, INITIAL_BOOTSTRAP) == [grant['source_main']],
             'Pilot repair did not follow the trusted bootstrap')
        verify_hotfix(api, repair_sha, APPROVED_HOTFIX, comments)
        verify_compatibility(api, base['sha'], comments)
    else:
        need(parents(api, base['sha']) == [expected_parent],
             'Migration bootstrap no longer applies to this base')
    issue = api.call(f'/issues/{issue_number}')
    completed = issue.get('state') == 'closed' and issue.get('state_reason') == 'completed'
    need('pull_request' not in issue and (completed if repairing else
         issue.get('state') == 'open' or completed), 'Migration or maintenance issue is unavailable')
    if repairing:
        record = accepted.get('9') or {}
        need(record.get('pr') == repair['accepted_pr'] and record.get('head_sha') == repair['accepted_head'],
             'Original F00-V0 acceptance differs from the grant')
        gate.verify_acceptance(task, record, api, plan)
    files = api.pages(f"/pulls/{pr['number']}/files")
    actual = sorted(item['filename'] for item in files)
    need(len(actual) == pr['changed_files'] and len(actual) == len(set(actual))
         and actual == entry['paths'] and not any(item.get('previous_filename') for item in files),
         'Migration paths differ from the exact reviewed manifest')
    ids = gate.validate_plan(plan)
    native = api.pages(f'/issues/{issue_number}/dependencies/blocked_by')
    need({row['number'] for row in native} == set(task['dependency_issues']),
         'Native migration dependencies disagree with the trusted registry')
    for key in task['dependencies']:
        dependency = ids[key]
        gate.verify_acceptance(dependency, accepted.get(str(dependency['issue_number'])), api, plan)
    need(owner_marker(comments, f"GENESIS-OWNER-APPROVED: {head['sha']}"),
         'Missing exact project owner authorization')
    if readiness:
        names = gate.required_checks(task, files) | {'pilot-checks'}
        if repair is not None and not repairing:
            base_runs = api.pages(f"/commits/{repair_sha}/check-runs?filter=latest", key='check_runs')
            check(base_runs, 'pilot-checks', repair_sha)
            CandidateChecks(api, pr).wait(names)
        else:
            runs = api.pages(f"/commits/{head['sha']}/check-runs?filter=latest", key='check_runs')
            for name in sorted(names):
                check(runs, name, head['sha'])
    return f'{task_id}: exact recovery scope verified; product rotation unaffected'


def check(runs, name, sha, after=None):
    matching = [run for run in runs if run.get('name') == name and run.get('head_sha') == sha
                and (run.get('app') or {}).get('id') == 15368
                and run['app'].get('slug') == 'github-actions'
                and (not after or (run.get('started_at') or '') >= after)]
    gate.require(matching and all(run['status'] == 'completed' and run['conclusion'] == 'success'
                                  for run in matching), 'Missing/failed GitHub Actions check: ' + name)


def current_pr(api, number, expected_head, policy_sha):
    live = api.call('/git/ref/heads/main')
    gate.require(live['ref'] == 'refs/heads/main' and live['object']['type'] == 'commit'
                 and live['object']['sha'] == policy_sha, 'Trusted main moved; rerun against current main')
    pr = api.call(f'/pulls/{number}')
    gate.same_revision(pr, expected_head)
    # A pull response can retain its earlier base snapshot after a direct base push.
    # The workflow checks out main, and the canonical ref independently pins that checkout.
    return dict(pr, base=dict(pr['base'], sha=policy_sha))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pr', type=int, required=True)
    parser.add_argument('--mode', choices=['dependencies', 'readiness'], default='dependencies')
    parser.add_argument('--expected-head', required=True)
    parser.add_argument('--policy-sha', required=True)
    args = parser.parse_args()
    try:
        if V3.is_file():
            return gate.main()
        api = gate.GitHub()
        pr = api.call(f'/pulls/{args.pr}')
        if pr['head']['ref'] not in (BRANCH, REPAIR_BRANCH):
            return gate.main()
        pr = current_pr(api, args.pr, args.expected_head, args.policy_sha)
        grant = json.loads(Path(__file__).with_name('v3_activation_grant.json').read_bytes())
        plan = json.loads((ROOT / '.github/task-plan.json').read_bytes())
        accepted = json.loads((ROOT / '.github/acceptance.json').read_bytes())['accepted']
        result = verify(pr, plan, accepted, api, grant, args.mode == 'readiness')
        current_pr(api, args.pr, args.expected_head, args.policy_sha)
        print(result)
    except (gate.Rejected, RuntimeError, KeyError, TypeError, ValueError, OSError) as exc:
        raise SystemExit('GENESIS ACTIVATION BLOCKED: ' + str(exc)) from None


if __name__ == '__main__':
    main()
