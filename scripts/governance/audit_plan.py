"""Read-only audit of live issue metadata and native graph against the reviewed registry."""
import json
from pathlib import Path
from github_api import GitHub
from gate import validate_plan

def audit(plan, api):
    validate_plan(plan)
    issues, parents, errors = {}, {}, []
    for epic in plan['epics']:
        for issue in api.pages(f"/issues/{epic['number']}/sub_issues"):
            n = issue['number']
            if n in parents:
                errors.append(f'#{n}: appears under multiple work packages')
            issues[n], parents[n] = issue, epic['number']
    for task in plan['tasks']:
        n = task['issue_number']
        issue = issues.get(n)
        if not issue or parents[n] != task['parent_issue']:
            errors.append(f'#{n}: missing or wrong native parent')
            continue
        assignees = {u['login'].lower() for u in issue.get('assignees', [])}
        # Transition is phased: old live issue assignees are not cleared until the
        # new gate and independent review are accepted; never pretend migration done.
        migrating = plan.get('assignment_migration', {}).get('status') != 'COMPLETE'
        if not migrating and assignees:
            errors.append(f'#{n}: unexpected fixed assignee')
        body = issue.get('body') or ''
        expected = [f"<!-- plan-id: {task['plan_id']} -->"] + [f'- {key}: {value}' for key, value in (
            ('Priority', task['priority']), ('Planned Start', task['start']),
            ('Target Date', task['target']))]
        if not migrating and any(label in body for label in
                                 ('- Primary Owner:', '- Supporting Developer:',
                                  '- Independent Reviewer:')):
            errors.append(f'#{n}: stale fixed owner in issue body')
        expected.append(f"- Estimated Effort: {task['effort_min']}–{task['effort_max']} person-hours; midpoint {task['estimated_effort']}.")
        if any(text not in body for text in expected):
            errors.append(f'#{n}: issue body no longer matches plan')
        native = {x['number'] for x in api.pages(f'/issues/{n}/dependencies/blocked_by')}
        if native != set(task['dependency_issues']):
            errors.append(f'#{n}: native prerequisite drift')
    return errors

def main():
    plan = json.loads(Path('.github/task-plan.json').read_text(encoding='utf-8'))
    errors = audit(plan, GitHub())
    if errors:
        raise SystemExit('\n'.join(errors))
    print(f"Checked {len(plan['tasks'])} task bodies, parent links and native prerequisite sets (assignment transition pending if set). "
          'Personal Project cells require a separate board audit.')

if __name__ == '__main__':
    main()
