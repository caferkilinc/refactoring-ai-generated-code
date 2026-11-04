"""Temporary trusted-main gate for one owner-authorized Genesis v3 activation."""
import argparse
import json
from pathlib import Path

import gate

ROOT = Path(__file__).resolve().parents[2]
REPAIR_BRANCH = 'fix/9-pilot-integrity-and-status'
BRANCH = 'chore/1-genesis-v3-phase1'
REPO = 'caferkilinc/refactoring-ai-generated-code'
OWNER = 'cakarburkayy'
V3 = ROOT / 'docs/governance/PROJECT_GENESIS_CODEX_NATIVE_PROTOCOL_V3.md'


def parents(api, revision):
    return [parent['sha'] for parent in api.call(f'/git/commits/{revision}')['parents']]


def owner_decision(pr, api):
    marker = f"GENESIS-OWNER-APPROVED: {pr['head']['sha']}"
    return any((c.get('user') or {}).get('login', '').casefold() == OWNER
               and (c.get('body') or '').strip() == marker
               for c in api.pages(f"/issues/{pr['number']}/comments"))


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
    expected_parent = grant.get('prior_bootstrap', grant['source_main'])
    if repair is not None and not repairing:
        repaired = api.call('/pulls/48')
        scope(repaired, repair, REPAIR_BRANCH)
        need(repaired.get('merged') and repaired.get('merge_commit_sha') == base['sha']
             and repaired.get('merged_at') and owner_decision(repaired, api), 'PR #48 must be approved and merged to the current base')
        merged_parents = parents(api, base['sha'])
        need(len(merged_parents) == 2 and merged_parents[1] == repair['head'],
             'Pilot repair merge parents differ from the grant')
        need(parents(api, merged_parents[0]) == [expected_parent],
             'Pilot repair did not follow the trusted bootstrap')
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
    need(owner_decision(pr, api), 'Missing exact project owner authorization')
    if readiness:
        repair_time = repaired['merged_at'] if repair is not None and not repairing else None
        if repair_time:
            base_runs = api.pages(f"/commits/{base['sha']}/check-runs?filter=latest", key='check_runs')
            check(base_runs, 'pilot-checks', base['sha'])
        runs = api.pages(f"/commits/{head['sha']}/check-runs?filter=latest", key='check_runs')
        for name in sorted(gate.required_checks(task, files) | {'pilot-checks'}):
            check(runs, name, head['sha'], repair_time if name == 'pilot-checks' else None)
    return f'{task_id}: exact recovery scope verified; product rotation unaffected'


def check(runs, name, sha, after=None):
    matching = [run for run in runs if run.get('name') == name and run.get('head_sha') == sha
                and (run.get('app') or {}).get('id') == 15368
                and run['app'].get('slug') == 'github-actions'
                and (not after or (run.get('started_at') or '') >= after)]
    gate.require(matching and all(run['status'] == 'completed' and run['conclusion'] == 'success'
                                  for run in matching), 'Missing/failed GitHub Actions check: ' + name)


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
        gate.same_revision(pr, args.expected_head, args.policy_sha)
        grant = json.loads(Path(__file__).with_name('v3_activation_grant.json').read_bytes())
        plan = json.loads((ROOT / '.github/task-plan.json').read_bytes())
        accepted = json.loads((ROOT / '.github/acceptance.json').read_bytes())['accepted']
        result = verify(pr, plan, accepted, api, grant, args.mode == 'readiness')
        gate.same_revision(api.call(f'/pulls/{args.pr}'), args.expected_head, args.policy_sha)
        print(result)
    except (gate.Rejected, RuntimeError, KeyError, TypeError, ValueError, OSError) as exc:
        raise SystemExit('GENESIS ACTIVATION BLOCKED: ' + str(exc)) from None


if __name__ == '__main__':
    main()
