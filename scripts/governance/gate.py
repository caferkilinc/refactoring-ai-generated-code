"""Fail-closed prerequisite verification using policy checked out from trusted base."""
import argparse
import json
import re
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
    for task in tasks:
        require(task['owner'] != task['reviewer'], 'Reviewer must be independent')
        require(task['reviewer'] != task['support'], 'Reviewer cannot be supporting developer')
        require(task['start'] <= task['target'] < plan['deadline'], 'Invalid dates')
        require(task['effort_min'] <= task['estimated_effort'] <= task['effort_max'], 'Invalid estimate')
        require(task['allowed_paths'] and task['required_checks'], 'Missing scope/check policy')
        visit(task['plan_id'])
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

def check_paths(task, files):
    require(files, 'Changed files unavailable')
    for item in files:
        for path in [item['filename']] + ([item['previous_filename']] if item.get('previous_filename') else []):
            require(any(path.startswith(p) if p.endswith('/') else path == p
                        for p in task['allowed_paths']), 'Out-of-task path: ' + path)

def verify_acceptance(task, record, api, plan):
    require(isinstance(record, dict), f"#{task['issue_number']} missing trusted acceptance record")
    require(record.get('evidence') and all(urlparse(u).scheme == 'https' and urlparse(u).netloc
                                         for u in record['evidence']), 'Missing HTTPS evidence')
    issue = api.call(f"/issues/{task['issue_number']}")
    require(issue['state'] == 'closed' and issue.get('state_reason') == 'completed', 'Prerequisite not completed')
    require(isinstance(record.get('pr'), int), 'Missing acceptance PR number')
    pr = api.call(f"/pulls/{record['pr']}")
    require(pr.get('merged_at') and pr['base']['ref'] == 'main', 'Prerequisite PR is not merged to main')
    require(pr['base']['repo']['full_name'] == plan['repository'], 'Wrong repository')
    require(record.get('head_sha') == pr['head']['sha'], 'Accepted revision differs from PR head')
    require(linked_task(pr, plan)['plan_id'] == task['plan_id'], 'Accepted PR belongs to another task')
    check_paths(task, api.pages(f"/pulls/{record['pr']}/files"))
    reviews = api.pages(f"/pulls/{record['pr']}/reviews")
    latest = {}
    for review in reviews:
        if review['state'] in ('APPROVED', 'CHANGES_REQUESTED', 'DISMISSED'):
            latest[review['user']['login']] = review
    approved = False
    for user, review in latest.items():
        if (user.lower() != pr['user']['login'].lower() and
            user.lower() not in {task['owner'].lower(), task['support'].lower()} and
            user in plan['team'] and review['state'] == 'APPROVED' and
            review.get('commit_id') == pr['head']['sha']):
            permission = api.call('/collaborators/' + user + '/permission')['permission']
            approved |= permission in ('write', 'maintain', 'admin')
    require(approved, 'No current independent Write approval for accepted revision')
    checks = api.pages(f"/commits/{pr['head']['sha']}/check-runs?filter=latest", key='check_runs')
    for name in task['required_checks']:
        selected = [c for c in checks if c['name'] == name and c.get('app', {}).get('slug') == 'github-actions']
        require(selected and all(c['status'] == 'completed' and c['conclusion'] == 'success'
                                 for c in selected), 'Missing/failed GitHub Actions check: ' + name)

def evaluate(pr, plan, accepted, api):
    ids = validate_plan(plan)
    task = linked_task(pr, plan)
    issue = api.call(f"/issues/{task['issue_number']}")
    require('pull_request' not in issue, 'Task is a PR rather than issue')
    maintenance = (task['plan_id'] == 'F01-GOV' and issue.get('state') == 'closed'
                   and issue.get('state_reason') == 'completed')
    require(issue.get('state') == 'open' or maintenance, 'Implementation task must be open')
    check_paths(task, api.pages(f"/pulls/{pr['number']}/files"))
    # Live native dependencies supplement the base registry; missing native edges fail closed.
    native = api.pages(f"/issues/{task['issue_number']}/dependencies/blocked_by")
    native_numbers = {x['number'] for x in native}
    expected = set(task['dependency_issues'])
    require(native_numbers == expected, 'Native dependencies disagree with trusted task-plan')
    for dependency in task['dependencies']:
        dep = ids[dependency]
        verify_acceptance(dep, accepted.get(str(dep['issue_number'])), api, plan)
    return f"{task['plan_id']}: all {len(expected)} mandatory prerequisites accepted"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pr', required=True, type=int)
    args = parser.parse_args()
    plan = json.loads(Path('.github/task-plan.json').read_text())
    accepted = json.loads(Path('.github/acceptance.json').read_text())['accepted']
    api = GitHub()
    try:
        print(evaluate(api.call(f'/pulls/{args.pr}'), plan, accepted, api))
    except (Rejected, RuntimeError, KeyError, TypeError, ValueError) as exc:
        raise SystemExit('DEPENDENCY GATE BLOCKED: ' + str(exc)) from None

if __name__ == '__main__':
    main()
