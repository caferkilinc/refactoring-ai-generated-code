"""Temporary trusted-main gate for one owner-authorized Genesis v3 activation."""
import argparse
import json
from pathlib import Path

import gate

ROOT = Path(__file__).resolve().parents[2]
BRANCH = 'chore/1-genesis-v3-phase1'
REPO = 'caferkilinc/refactoring-ai-generated-code'
OWNER = 'cakarburkayy'
V3 = ROOT / 'docs/governance/PROJECT_GENESIS_CODEX_NATIVE_PROTOCOL_V3.md'


def verify(pr, plan, accepted, api, grant, readiness):
    need = gate.require
    head, base = pr['head'], pr['base']
    task = gate.linked_task(pr, plan)
    need(plan['repository'] == REPO and head['repo']['full_name'] == REPO
         and base['repo']['full_name'] == REPO and base['ref'] == 'main', 'Wrong migration repository')
    need(task['plan_id'] == 'F01-GOV' and task['issue_number'] == 1
         and pr['number'] == grant['pr'] and head['ref'] == BRANCH,
         'Wrong migration task, PR or branch')
    need(pr['user']['login'].casefold() == grant['author'] == OWNER, 'Wrong migration author')
    need(head['sha'] == grant['head'], 'Migration head is outside the trusted grant')
    need(pr['state'] == 'open' and not pr.get('draft') and not pr.get('merged'), 'Migration PR is not ready')
    parents = api.call(f"/git/commits/{base['sha']}")['parents']
    need([parent['sha'] for parent in parents] == [grant['source_main']],
         'Migration bootstrap no longer applies to this base')
    issue = api.call('/issues/1')
    need('pull_request' not in issue and (issue['state'] == 'open' or
         (issue['state'] == 'closed' and issue.get('state_reason') == 'completed')),
         'Migration issue is unavailable')
    files = api.pages(f"/pulls/{pr['number']}/files")
    actual = sorted(item['filename'] for item in files)
    need(len(actual) == pr['changed_files'] and len(actual) == len(set(actual))
         and actual == grant['paths'] and not any(item.get('previous_filename') for item in files),
         'Migration paths differ from the exact reviewed manifest')
    ids = gate.validate_plan(plan)
    native = api.pages('/issues/1/dependencies/blocked_by')
    need({row['number'] for row in native} == set(task['dependency_issues']),
         'Native migration dependencies disagree with the trusted registry')
    for key in task['dependencies']:
        dependency = ids[key]
        gate.verify_acceptance(dependency, accepted.get(str(dependency['issue_number'])), api, plan)
    comments = api.pages(f"/issues/{pr['number']}/comments")
    marker = f"GENESIS-OWNER-APPROVED: {head['sha']}"
    need(any((c.get('user') or {}).get('login', '').casefold() == OWNER
             and (c.get('body') or '').strip() == marker for c in comments),
         'Missing exact project owner authorization')
    if readiness:
        runs = api.pages(f"/commits/{head['sha']}/check-runs?filter=latest", key='check_runs')
        for name in sorted(gate.required_checks(task, files) | {'pilot-checks'}):
            matching = [run for run in runs if run.get('name') == name and run.get('head_sha') == head['sha']
                        and (run.get('app') or {}).get('id') == 15368
                        and run['app'].get('slug') == 'github-actions']
            need(matching and all(run['status'] == 'completed' and run['conclusion'] == 'success'
                                  for run in matching), 'Missing/failed GitHub Actions check: ' + name)
    return 'F01-GOV: exact one-time Genesis v3 activation verified; product rotation unaffected'


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
        if pr['head']['ref'] != BRANCH:
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
