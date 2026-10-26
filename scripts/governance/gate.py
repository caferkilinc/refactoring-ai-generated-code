"""Fail-closed prerequisite verification using policy checked out from trusted base."""
import argparse
import json
import re
import math
from datetime import date
from pathlib import Path
from urllib.parse import urlparse
from github_api import GitHub

class Rejected(Exception):
    pass

def require(value, message):
    if not value:
        raise Rejected(message)

def validate_plan(plan):
    tasks = plan['tasks']
    ids = {t['plan_id']: t for t in tasks}
    require(len(ids) == len(tasks), 'Duplicate Plan ID')
    require(len({t['issue_number'] for t in tasks}) == len(tasks), 'Duplicate issue')
    visiting, done = set(), set()
    def visit(key):
        require(key in ids, 'Unknown prerequisite ' + key)
        require(key not in visiting, 'Dependency cycle at ' + key)
        if key in done:
            return
        visiting.add(key)
        for dep in ids[key]['dependencies']:
            require(dep in ids, 'Unknown prerequisite ' + dep)
            require(not (ids[key]['priority'] == 'P0' and ids[dep]['priority'] == 'P1'),
                    'P1 must not block P0')
            visit(dep)
        visiting.remove(key)
        done.add(key)
    rotation = plan.get('sequential_execution', {})
    sequence = rotation.get('team_sequence', [])
    require(sequence == ['cakarburkayy', 'caferkilinc', 'Yaman-A-E',
                         'ismail-cevik', 'tahaugurtoyran'],
            'Invalid or altered five-member rotation')
    require(all(member in plan['team'] for member in sequence),
            'Unknown team member in rotation')
    require(rotation.get('rotation_index') in range(len(sequence)),
            'Invalid rotation index')
    require(rotation.get('active_owner') == sequence[rotation['rotation_index']],
            'Active owner disagrees with rotation index')
    require(rotation.get('active_task_plan_id') in ids,
            'Active task is not in trusted registry')
    require(rotation.get('next_owner_if_accepted') ==
            sequence[(rotation['rotation_index'] + 1) % len(sequence)],
            'Next owner disagrees with rotation')
    require(rotation.get('handoff_confirmed') is False,
            'Handoff cannot be pre-confirmed by task registry')
    require(not any(t.get(k) for t in tasks for k in ('owner', 'support', 'reviewer')),
            'Static developer assignments are forbidden')
    for task in tasks:
        require(type(task['issue_number']) is int and task['issue_number'] > 0, 'Invalid issue number')
        require(task['priority'] in ('P0', 'P1'), 'Unknown priority')
        require(task['kind'] in ('code', 'research', 'documentation'), 'Unknown task kind')
        require(date.fromisoformat(task['start']) <= date.fromisoformat(task['target'])
                < date.fromisoformat(plan['deadline']), 'Invalid dates')
        require(all(type(task[k]) in (int, float) and math.isfinite(task[k]) and task[k] > 0
                    for k in ('effort_min', 'estimated_effort', 'effort_max')), 'Invalid estimate')
        require(task['effort_min'] <= task['estimated_effort'] <= task['effort_max'], 'Invalid estimate')
        require(task['allowed_paths'] and task['required_checks'], 'Missing scope/check policy')
        visit(task['plan_id'])
        require(len(set(task['dependencies'])) == len(task['dependencies']), 'Duplicate prerequisite')
        require(task['dependency_issues'] == [ids[d]['issue_number'] for d in task['dependencies']],
                'Plan IDs and native issue prerequisites disagree')
        require(any(e['id'] == task['work_package'] and e['number'] == task['parent_issue']
                    for e in plan['epics']), 'Wrong parent work package')
    return ids

def linked_task(pr, plan):
    match = re.fullmatch(r'(?:feature|fix|docs|test|chore)/(\d+)-[a-z0-9][a-z0-9-]*', pr['head']['ref'])
    require(match, 'Use a numbered topic branch')
    numbers = re.findall(r'^Task: #([0-9]+)\s*$', pr.get('body') or '', re.M)
    require(len(numbers) == 1 and numbers[0] == match[1], 'Task line and branch disagree')
    task = next((t for t in plan['tasks'] if t['issue_number'] == int(match[1])), None)
    require(task, 'Issue is not registered in trusted base task-plan')
    plans = re.findall(r'^Plan: ([A-Z0-9-]+)\s*$', pr.get('body') or '', re.M)
    require(plans == [task['plan_id']], 'Plan line disagrees with trusted registry')
    return task

def check_paths(task, files, pr=None):
    require(files, 'Changed files unavailable')
    if pr is not None:
        require(type(pr.get('changed_files')) is int and len(files) == pr['changed_files']
                and len({i['filename'] for i in files}) == len(files),
                'Incomplete changed-file list; refusing partial scope validation')
    for item in files:
        for path in [item['filename']] + ([item['previous_filename']] if item.get('previous_filename') else []):
            protected = path.startswith(('scripts/governance/', 'tests/governance/')) or path in (
                '.github/CODEOWNERS', '.github/task-plan.json', '.github/acceptance.json',
                'AGENTS.md', '.agents/skills/development-handoff/SKILL.md',
                '.github/branch-protection.proposed.json', '.github/workflows/governance-ci.yml',
                '.github/workflows/dependency-gate.yml', '.github/workflows/issue-graph-sync.yml',
                '.github/workflows/live-plan-audit.yml')
            require(not protected or task['plan_id'] == 'F01-GOV',
                    'Governance policy changes require the governance task: ' + path)
            require(any(path.startswith(p) if p.endswith('/') else path == p
                        for p in task['allowed_paths']), 'Out-of-task path: ' + path)

def independent_review(task, pr, api, plan):
    """Same review rule before merge and before downstream acceptance."""
    reviews = api.pages(f"/pulls/{pr['number']}/reviews")
    latest = {}
    for review in reviews:
        if review['state'] in ('APPROVED', 'CHANGES_REQUESTED', 'DISMISSED'):
            latest[review['user']['login'].lower()] = review
    team = {user.lower() for user in plan['team']}
    # Review independence is based on actual PR author/committers, not historical task owners.
    excluded = {pr['user']['login'].lower()}
    for commit in api.pages(f"/pulls/{pr['number']}/commits"):
        for field in ('author', 'committer'):
            user = commit.get(field) or {}
            if user.get('login'):
                excluded.add(user['login'].lower())
    approved = False
    for user, review in latest.items():
        if user not in team or user in excluded:
            continue
        permission = api.call('/collaborators/' + review['user']['login'] + '/permission')['permission']
        if permission not in ('write', 'maintain', 'admin'):
            continue
        require(review['state'] != 'CHANGES_REQUESTED', 'Unresolved independent changes request')
        approved |= review['state'] == 'APPROVED' and review.get('commit_id') == pr['head']['sha']
    require(approved, 'No current independent Write approval for this revision')

def required_checks(task, files):
    """Do not let a frontend-labelled task hide backend changes, or vice versa."""
    names = set(task['required_checks'])
    paths = [i['filename'] for i in files]
    if any(p.startswith('frontend/') for p in paths):
        names.add('frontend-checks')
    if any(p.startswith('backend/') and not p.startswith('backend/core/schemas/') for p in paths):
        names.add('backend-checks')
    if any(p.startswith('backend/core/schemas/') or p.startswith('tests/contracts/') for p in paths):
        names.add('contract-checks')
    return names

def successful_checks(task, pr, files, api, ci_sha=None):
    sha = ci_sha or pr['head']['sha']
    allowed = {pr['head']['sha']}
    if pr.get('merged_at') and pr.get('merge_commit_sha'):
        allowed.add(pr['merge_commit_sha'])
    require(sha in allowed, 'CI revision is unrelated to the accepted PR')
    checks = api.pages(f'/commits/{sha}/check-runs?filter=latest', key='check_runs')
    for name in required_checks(task, files):
        selected = [c for c in checks if c['name'] == name and c.get('app', {}).get('slug') == 'github-actions']
        require(selected and all(c['status'] == 'completed' and c['conclusion'] == 'success'
                                 for c in selected), 'Missing/failed GitHub Actions check: ' + name)

def verify_acceptance(task, record, api, plan):
    require(isinstance(record, dict), f"#{task['issue_number']} missing trusted acceptance record")
    evidence = record.get('evidence')
    require(isinstance(evidence, list) and evidence and all(
        isinstance(u, str) and urlparse(u).scheme == 'https' and urlparse(u).netloc
        and not urlparse(u).username and not urlparse(u).password for u in evidence), 'Missing HTTPS evidence')
    issue = api.call(f"/issues/{task['issue_number']}")
    require(issue['state'] == 'closed' and issue.get('state_reason') == 'completed', 'Prerequisite not completed')
    require(type(record.get('pr')) is int and record['pr'] > 0, 'Missing acceptance PR number')
    pr = api.call(f"/pulls/{record['pr']}")
    require(pr.get('merged_at') and pr['base']['ref'] == 'main', 'Prerequisite PR is not merged to main')
    require(pr['base']['repo']['full_name'] == plan['repository'], 'Wrong repository')
    require(record.get('head_sha') == pr['head']['sha'], 'Accepted revision differs from PR head')
    require(linked_task(pr, plan)['plan_id'] == task['plan_id'], 'Accepted PR belongs to another task')
    files = api.pages(f"/pulls/{record['pr']}/files")
    check_paths(task, files, pr)
    independent_review(task, pr, api, plan)
    successful_checks(task, pr, files, api, record.get('ci_sha'))

def evaluate(pr, plan, accepted, api):
    ids = validate_plan(plan)
    task = linked_task(pr, plan)
    issue = api.call(f"/issues/{task['issue_number']}")
    require('pull_request' not in issue, 'Task is a PR rather than issue')
    maintenance = (task['plan_id'] == 'F01-GOV' and issue.get('state') == 'closed'
                   and issue.get('state_reason') == 'completed')
    require(issue.get('state') == 'open' or maintenance, 'Implementation task must be open')
    require(pr['base']['repo']['full_name'] == plan['repository'] and pr['base']['ref'] == 'main',
            'Wrong integration target')
    rotation = plan['sequential_execution']
    require(task['plan_id'] == rotation['active_task_plan_id'],
            'PR task is not the single authorized active task')
    require(pr['user']['login'].lower() == rotation['active_owner'].lower(),
            'PR author is not the authorized active developer')
    check_paths(task, api.pages(f"/pulls/{pr['number']}/files"), pr)
    # Live native dependencies supplement the base registry; missing native edges fail closed.
    native = api.pages(f"/issues/{task['issue_number']}/dependencies/blocked_by")
    native_numbers = {x['number'] for x in native}
    expected = set(task['dependency_issues'])
    require(native_numbers == expected, 'Native dependencies disagree with trusted task-plan')
    for dependency in task['dependencies']:
        dep = ids[dependency]
        verify_acceptance(dep, accepted.get(str(dep['issue_number'])), api, plan)
    return f"{task['plan_id']}: all {len(expected)} mandatory prerequisites accepted"

def readiness(pr, plan, accepted, api):
    result = evaluate(pr, plan, accepted, api)
    require(pr.get('state') == 'open' and not pr.get('draft'), 'PR must be open and ready for review')
    task = linked_task(pr, plan)
    files = api.pages(f"/pulls/{pr['number']}/files")
    independent_review(task, pr, api, plan)
    successful_checks(task, pr, files, api)
    return result + '; current independent review and applicable CI verified'

def same_revision(pr, expected_head=None, policy_sha=None):
    if expected_head:
        require(pr['head']['sha'] == expected_head, 'PR head moved; use the new event run')
    if policy_sha:
        require(pr['base']['sha'] == policy_sha, 'Trusted main moved; rerun against current main')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pr', required=True, type=int)
    parser.add_argument('--mode', choices=['dependencies', 'readiness'], default='dependencies')
    parser.add_argument('--expected-head')
    parser.add_argument('--policy-sha')
    args = parser.parse_args()
    try:
        plan = json.loads(Path('.github/task-plan.json').read_text(encoding='utf-8'))
        accepted = json.loads(Path('.github/acceptance.json').read_text(encoding='utf-8'))['accepted']
        api = GitHub()
        pr = api.call(f'/pulls/{args.pr}')
        same_revision(pr, args.expected_head, args.policy_sha)
        result = (readiness if args.mode == 'readiness' else evaluate)(pr, plan, accepted, api)
        same_revision(api.call(f'/pulls/{args.pr}'), pr['head']['sha'], pr['base'].get('sha'))
        print(result)
    except (Rejected, RuntimeError, KeyError, TypeError, ValueError) as exc:
        raise SystemExit('DEPENDENCY GATE BLOCKED: ' + str(exc)) from None

if __name__ == '__main__':
    main()
