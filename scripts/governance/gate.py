"""Fail-closed prerequisite verification using policy checked out from trusted base."""
import argparse
import base64
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
    require(set(sequence) == set(plan['team']),
            'Unknown team member in rotation')
    require(type(rotation.get('rotation_index')) is int and rotation['rotation_index'] in range(len(sequence)),
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
    require(not any(k in t for t in tasks for k in ('owner', 'support', 'reviewer')),
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

def changed_paths(files):
    for item in files:
        yield item['filename']
        if item.get('previous_filename'):
            yield item['previous_filename']

def governance_path(path):
    return path.startswith(('scripts/governance/', 'tests/governance/', 'docs/governance/',
                            '.agents/skills/', '.github/issue_template/')) or path in {
        '.github/codeowners', '.github/task-plan.json', '.github/acceptance.json',
        '.github/pull_request_template.md', '.github/branch-protection.proposed.json',
        '.github/workflows/governance-ci.yml', '.github/workflows/dependency-gate.yml',
        '.github/workflows/issue-graph-sync.yml', '.github/workflows/live-plan-audit.yml',
        'agents.md', 'contributing.md', 'docs/team_workflow.md', 'docs/dependency_management.md',
    }

def protected_path(path):
    path = path.casefold()
    return governance_path(path) or path.startswith((
        '.github/workflows/', '.github/actions/', 'docs/decisions/', 'experiments/original-ai-code/',
        'experiments/java-pilot/manifests/', 'experiments/java-pilot/provenance/', 'tests/fixtures/',
    )) or path in {'.gitattributes', '.gitignore', 'docs/srs.md', 'docs/srs_en.md',
                  'docs/architecture.md', 'security.md'}

def check_paths(task, files, pr=None):
    require(files, 'Changed files unavailable')
    if pr is not None:
        require(type(pr.get('changed_files')) is int and len(files) == pr['changed_files']
                and len({i['filename'] for i in files}) == len(files),
                'Incomplete changed-file list; refusing partial scope validation')
    for path in changed_paths(files):
        require(not governance_path(path.casefold()) or task['plan_id'] == 'F01-GOV',
                'Governance policy changes require the governance task: ' + path)
        continuity = {'report.md', 'docs/PROJECT_STATUS.md', 'docs/DEVELOPMENT_ROADMAP.md'}
        require(path in continuity or any(
            path.startswith(p) if p.endswith('/') else path == p
            for p in task['allowed_paths']), 'Out-of-task path: ' + path)

def has_comment(comments, login, marker):
    return any(
        (c.get('user') or {}).get('login', '').lower() == login.lower()
        and (c.get('body') or '').strip() == marker
        for c in comments
    )

def delegated_revision(task, pr, plan):
    # ADR 0006 is a historical grant tied to exactly this PR and head.
    delegated_revision = 'd923134da4f9f5a2ab55a5f51fbf9415ff717262'
    repository = 'caferkilinc/refactoring-ai-generated-code'
    return (
        plan['repository'] == repository
        and task['plan_id'] == 'F00-V0' and task['issue_number'] == 9
        and pr['number'] == 45
        and pr['head']['sha'] == delegated_revision
        and pr['head']['ref'] == 'feature/9-java-v0-pilot'
        and (pr['head'].get('repo') or {}).get('full_name') == repository
        and pr['base']['ref'] == 'main'
        and pr['base']['repo']['full_name'] == repository
        and pr['user']['login'].lower() == 'caferkilinc'
    )

def owner_approval(task, pr, api, plan):
    """Verify the v2 owner marker or the narrowly scoped ADR 0006 grant."""
    sha = pr['head']['sha']
    comments = api.pages(f"/issues/{pr['number']}/comments")
    require(has_comment(comments, 'cakarburkayy', 'GENESIS-OWNER-APPROVED: ' + sha)
            or (delegated_revision(task, pr, plan)
                and has_comment(comments, 'caferkilinc', 'GENESIS-DELEGATE-APPROVED: ' + sha)),
            'Missing current Burkay owner approval for this PR revision; '
            'ADR 0006 delegated approval is limited to PR #45 at its recorded SHA')

def publication_approval(task, pr, files, api, plan, developer):
    head = pr['head']
    repository = plan['repository']
    require(developer in plan['sequential_execution']['team_sequence']
            and pr['user']['login'].lower() == developer.lower(),
            'Publication must belong to the authorized developer')
    require((head.get('repo') or {}).get('full_name') == repository,
            'Developer approval requires a branch in the canonical repository')
    require(re.fullmatch(r'[0-9a-f]{40}', head['sha']), 'Invalid PR head revision')
    comments = api.pages(f"/issues/{pr['number']}/comments")
    marker = (f"GENESIS-DEVELOPER-APPROVED: {task['plan_id']} {repository} "
              f"{head['ref']} {head['sha']} merge")
    require(has_comment(comments, developer, marker),
            'Missing authorized developer approval for this task, repository, branch, revision and merge scope')
    if task['plan_id'] == 'F01-GOV' or any(protected_path(p) for p in changed_paths(files)):
        require(has_comment(comments, 'cakarburkayy', 'GENESIS-OWNER-APPROVED: ' + head['sha']),
                'Protected changes require separate current Burkay owner approval')


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
    if 'developer' in record:
        publication_approval(task, pr, files, api, plan, record['developer'])
    else:
        # Existing trusted v2 records keep their original approval evidence.
        owner_approval(task, pr, api, plan)
    successful_checks(task, pr, files, api, record.get('ci_sha'))
    return pr

def check_dependencies(task, ids, accepted, api, plan):
    native = api.pages(f"/issues/{task['issue_number']}/dependencies/blocked_by")
    expected = set(task['dependency_issues'])
    require({x['number'] for x in native} == expected,
            'Native dependencies disagree with trusted task-plan')
    for dependency in task['dependencies']:
        dep = ids[dependency]
        verify_acceptance(dep, accepted.get(str(dep['issue_number'])), api, plan)
    return len(expected)

def bootstrap_pr(task, pr):
    # Historical PR #38 remains auditable and never consumes a rotation turn.
    return (pr['number'] == 38 and task['plan_id'] == 'F01-GOV'
            and pr['head']['ref'] == 'chore/1-team-workflow'
            and pr['user']['login'].lower() == 'caferkilinc')

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
    if not bootstrap_pr(task, pr):
        require(task['plan_id'] == rotation['active_task_plan_id'],
                'PR task is not the single authorized active task')
        require(pr['user']['login'].lower() == rotation['active_owner'].lower(),
                'PR author is not the authorized active developer')
    check_paths(task, api.pages(f"/pulls/{pr['number']}/files"), pr)
    count = check_dependencies(task, ids, accepted, api, plan)
    return f"{task['plan_id']}: all {count} mandatory prerequisites accepted"

def readiness(pr, plan, accepted, api):
    result = evaluate(pr, plan, accepted, api)
    require(pr.get('state') == 'open' and not pr.get('draft'), 'PR must be open and ready for review')
    task = linked_task(pr, plan)
    files = api.pages(f"/pulls/{pr['number']}/files")
    check_paths(task, files, pr)
    if bootstrap_pr(task, pr) or delegated_revision(task, pr, plan):
        owner_approval(task, pr, api, plan)
    else:
        publication_approval(task, pr, files, api, plan, plan['sequential_execution']['active_owner'])
    successful_checks(task, pr, files, api)
    return result + '; current revision approval and applicable CI verified'

def propose_handoff(pr, plan, accepted, record, api, policy_sha):
    """Validate a handoff and return a read-only rotation proposal."""
    ids = validate_plan(plan)
    task = linked_task(pr, plan)
    rotation = plan['sequential_execution']
    sha = pr['head']['sha']
    key = f"{task['plan_id']}:{sha}"
    require(record.get('pr') == pr['number'] and record.get('head_sha') == sha,
            'Handoff record does not match PR and revision')
    existing = accepted.get(str(task['issue_number']))
    if existing is not None:
        require(existing.get('head_sha') == sha and existing.get('pr') == pr['number'],
                'Task already accepted at another revision; requires protected reconciliation')
        verify_acceptance(task, existing, api, plan)
        return {'status': 'ALREADY_ACCEPTED', 'handoff_key': key, 'advance': False}
    require(key != rotation.get('last_accepted_handoff_key'),
            'Handoff key already used but acceptance record is missing')
    require(task['plan_id'] != 'F01-GOV' and task['plan_id'] == rotation['active_task_plan_id']
            and record.get('developer') == rotation['active_owner'],
            'Only the active ordinary task and developer may propose a new handoff')
    merged = verify_acceptance(task, record, api, plan)
    merge_sha = merged.get('merge_commit_sha') or ''
    require(re.fullmatch(r'[0-9a-f]{40}', merge_sha), 'Missing merged revision')
    ancestry = api.call(f'/compare/{merge_sha}...{policy_sha}')
    require(ancestry.get('status') in ('ahead', 'identical')
            and (ancestry.get('merge_base_commit') or {}).get('sha') == merge_sha,
            'Merged revision is not reachable from verified main')
    check_dependencies(task, ids, accepted, api, plan)
    sequence = rotation['team_sequence']
    next_index = (rotation['rotation_index'] + 1) % len(sequence)
    return {'status': 'REVIEW_REQUIRED', 'handoff_key': key, 'advance': False,
            'proposed_index': next_index, 'proposed_owner': sequence[next_index]}

def same_revision(pr, expected_head=None, policy_sha=None):
    if expected_head:
        require(pr['head']['sha'] == expected_head, 'PR head moved; use the new event run')
    if policy_sha:
        require(pr['base']['sha'] == policy_sha, 'Trusted main moved; rerun against current main')

def policy_at(api, path, sha):
    content = api.call(f'/contents/{path}?ref={sha}')
    require(content.get('encoding') == 'base64', 'Trusted policy content unavailable: ' + path)
    return json.loads(base64.b64decode(content['content']))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pr', required=True, type=int)
    parser.add_argument('--mode', choices=['dependencies', 'readiness', 'handoff'], default='dependencies')
    parser.add_argument('--expected-head')
    parser.add_argument('--policy-sha')
    parser.add_argument('--handoff-record', type=Path)
    args = parser.parse_args()
    try:
        api = GitHub()
        pr = api.call(f'/pulls/{args.pr}')
        if args.mode == 'handoff':
            require(args.handoff_record and args.policy_sha
                    and re.fullmatch(r'[0-9a-f]{40}', args.policy_sha),
                    'Handoff requires --handoff-record and verified --policy-sha')
            require(api.call('/git/ref/heads/main')['object']['sha'] == args.policy_sha,
                    'Trusted main moved; reread policy and evidence')
            plan = policy_at(api, '.github/task-plan.json', args.policy_sha)
            accepted = policy_at(api, '.github/acceptance.json', args.policy_sha)['accepted']
            same_revision(pr, args.expected_head)
            record = json.loads(args.handoff_record.read_text(encoding='utf-8'))
            require(isinstance(record, dict), 'Invalid handoff record')
            result = json.dumps(propose_handoff(pr, plan, accepted, record, api, args.policy_sha))
            require(api.call('/git/ref/heads/main')['object']['sha'] == args.policy_sha,
                    'Trusted main moved during handoff verification')
            same_revision(api.call(f'/pulls/{args.pr}'), pr['head']['sha'])
        else:
            plan = json.loads(Path('.github/task-plan.json').read_text(encoding='utf-8'))
            accepted = json.loads(Path('.github/acceptance.json').read_text(encoding='utf-8'))['accepted']
            same_revision(pr, args.expected_head, args.policy_sha)
            result = (readiness if args.mode == 'readiness' else evaluate)(pr, plan, accepted, api)
            same_revision(api.call(f'/pulls/{args.pr}'), pr['head']['sha'], pr['base'].get('sha'))
        print(result)
    except (Rejected, RuntimeError, KeyError, TypeError, ValueError, OSError) as exc:
        raise SystemExit('DEPENDENCY GATE BLOCKED: ' + str(exc)) from None

if __name__ == '__main__':
    main()
