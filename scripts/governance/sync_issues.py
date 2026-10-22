"""Idempotent native subissue/dependency sync. Owner-only bootstrap workflow."""
import json
from pathlib import Path
from github_api import GitHub
from gate import validate_plan

def main():
    plan = json.loads(Path('.github/task-plan.json').read_text())
    validate_plan(plan)
    api = GitHub()
    for name, color, description in [
        ('type:bug', 'd73a4a', 'Reproducible defect in an implemented capability'),
        ('type:feature', 'a2eeef', 'Proposed capability requiring scope and plan review')]:
        if api.call('/labels/' + name, missing_ok=True) is None:
            api.call('/labels', 'POST', {'name': name, 'color': color, 'description': description})
    numbers = {t['issue_number'] for t in plan['tasks']} | {e['number'] for e in plan['epics']}
    issues = {n: api.call(f'/issues/{n}') for n in numbers}
    for task in plan['tasks']:
        n, parent = task['issue_number'], task['parent_issue']
        old_parent = api.call(f'/issues/{n}/parent', missing_ok=True)
        if old_parent is None:
            api.call(f'/issues/{parent}/sub_issues', 'POST', {'sub_issue_id': issues[n]['id']})
        elif old_parent['number'] != parent:
            raise RuntimeError(f'Unexpected parent for #{n}; refusing to reparent')
        old = {x['number'] for x in api.pages(f'/issues/{n}/dependencies/blocked_by')}
        expected = set(task['dependency_issues'])
        if old - expected:
            raise RuntimeError(f'Unexpected native prerequisites for #{n}; refusing deletion')
        for dep in sorted(expected - old):
            api.call(f'/issues/{n}/dependencies/blocked_by', 'POST', {'issue_id': issues[dep]['id']})
        print(f'#{n}: parent #{parent}; prerequisites {sorted(expected)}')

if __name__ == '__main__':
    main()
