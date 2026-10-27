"""Idempotent native subissue/dependency sync. Owner-only bootstrap workflow."""
import json
from pathlib import Path
from github_api import GitHub
from gate import validate_plan

def preflight(plan, api):
    """Read the entire graph before making the first external change."""
    validate_plan(plan)
    numbers = {t['issue_number'] for t in plan['tasks']} | {e['number'] for e in plan['epics']}
    issues = {n: api.call(f'/issues/{n}') for n in numbers}
    operations = []
    for task in plan['tasks']:
        n, parent = task['issue_number'], task['parent_issue']
        old_parent = api.call(f'/issues/{n}/parent', missing_ok=True)
        if old_parent is None:
            operations.append((f'/issues/{parent}/sub_issues', {'sub_issue_id': issues[n]['id']}))
        elif old_parent['number'] != parent:
            raise RuntimeError(f'Unexpected parent for #{n}; refusing to reparent')
        old = {x['number'] for x in api.pages(f'/issues/{n}/dependencies/blocked_by')}
        expected = set(task['dependency_issues'])
        if old - expected:
            raise RuntimeError(f'Unexpected native prerequisites for #{n}; refusing deletion')
        for dep in sorted(expected - old):
            operations.append((f'/issues/{n}/dependencies/blocked_by', {'issue_id': issues[dep]['id']}))
    return operations

def synchronize(plan, api):
    operations = preflight(plan, api)
    for name, color, description in [
        ('type:bug', 'd73a4a', 'Reproducible defect in an implemented capability'),
        ('type:feature', 'a2eeef', 'Proposed capability requiring scope and plan review')]:
        if api.call('/labels/' + name, missing_ok=True) is None:
            api.call('/labels', 'POST', {'name': name, 'color': color, 'description': description})
    for path, data in operations:
        api.call(path, 'POST', data)
    for task in plan['tasks']:
        n, parent, expected = task['issue_number'], task['parent_issue'], task['dependency_issues']
        print(f'#{n}: parent #{parent}; prerequisites {sorted(expected)}')

def main():
    plan = json.loads(Path('.github/task-plan.json').read_text(encoding='utf-8'))
    synchronize(plan, GitHub())

if __name__ == '__main__':
    main()
