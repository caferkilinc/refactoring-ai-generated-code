"""Publish one reviewed ordinary Genesis task under already activated policy."""
import argparse
import base64
import hashlib
import json
import os
import re
import subprocess
import time
from pathlib import Path
from urllib.parse import quote, urlencode

import gate
from gate import Rejected, require
from github_api import GitHub
from task_execution import REPO, URLS, Repository, decide, digest, path_list


OWNER = 'cakarburkayy'
GOVERNANCE = {'governance-tests', 'documentation-checks', 'security-checks'}
TRUSTED_GATES = {'dependency-gate', 'merge-readiness'}
HOSTED = GOVERNANCE | TRUSTED_GATES | {'pilot-checks'}
HTTPS_URLS = {url for url in URLS if url.startswith('https://')}
GITHUB_ACTIONS_APP = 15368


def sha_bytes(content):
    return hashlib.sha256(content).hexdigest()


def ref(api, branch):
    data = api.call('/git/ref/heads/' + quote(branch, safe='/'), missing_ok=True)
    if data is None:
        return None
    require(data['ref'] == 'refs/heads/' + branch and data['object']['type'] == 'commit',
            'Unexpected GitHub ref')
    return data['object']['sha']


def active_protection(api):
    rule = api.call('/branches/main/protection')
    checks = rule.get('required_status_checks') or {}
    reviews = rule.get('required_pull_request_reviews')
    sources = {item['context']: item.get('app_id') for item in checks.get('checks', [])}
    contexts = set(checks.get('contexts', [])) | sources.keys()
    require(isinstance(reviews, dict) and checks.get('strict') is True and HOSTED <= contexts,
            'Classic main protection must require PRs, strict updates and the six publication checks')
    require(all(sources.get(name) == GITHUB_ACTIONS_APP for name in contexts),
            'Required checks must be pinned to the GitHub Actions app')
    require(not api.pages('/rules/branches/main'),
            'Additional rulesets require reconciliation before this classic-protection publisher can run')
    require((rule.get('enforce_admins') or {}).get('enabled') is True
            and (rule.get('allow_force_pushes') or {}).get('enabled') is False
            and (rule.get('allow_deletions') or {}).get('enabled') is False
            and (rule.get('required_conversation_resolution') or {}).get('enabled') is True,
            'Main protection must apply to administrators and forbid force pushes and deletion')
    require('bypass_pull_request_allowances' not in reviews
            or not any(reviews['bypass_pull_request_allowances'].values()),
            'Main permits a pull request bypass')
    require(not (rule.get('required_linear_history') or {}).get('enabled'),
            'Exact-head merge commit is incompatible with required linear history')
    return contexts, any(reviews.get(key) for key in (
        'required_approving_review_count', 'require_code_owner_reviews', 'require_last_push_approval'))


def trusted_activation(repo, main):
    for name in ('safe_publish.py', 'gate.py', 'github_api.py', 'task_execution.py'):
        relative = 'scripts/governance/' + name
        require(repo.blob(main, relative) == (repo.root / relative).read_bytes(),
                f'Publisher policy differs from trusted main: {relative}')
    repo.blob(main, 'docs/governance/PROJECT_GENESIS_CODEX_NATIVE_PROTOCOL_V3.md')


def diff_paths(repo, *args):
    return sorted(repo.git(*args, '--no-renames', '--name-only', '-z').decode().split('\0')[:-1])


def verify_blobs(repo, source, files):
    for path, state in files.items():
        result = repo.git('--literal-pathspecs', 'ls-files', '--stage', '-z', '--', path) if source == ':' else repo.git(
            '--literal-pathspecs', 'ls-tree', '-z', source, '--', path)
        if state is None:
            require(not result, f'Deletion was not recorded: {path}')
            continue
        require(result and result.startswith((b'100644 ', b'100755 ')),
                f'Unsupported or missing staged entry: {path}')
        spec = f':{path}' if source == ':' else f'{source}:{path}'
        require(sha_bytes(repo.git('show', spec)) == state[1],
                f'Git content differs from the reviewed bytes: {path}')
        if os.name != 'nt':
            require(result.startswith(b'100755 ') == bool(state[0] & 0o100),
                    f'Git executable mode differs from review: {path}')


def commit_reviewed(repo, contract, files, actor):
    paths = sorted(files)
    base = contract['base_revision']
    current = repo.text('rev-parse', 'HEAD')
    require(repo.text('branch', '--show-current') == contract['branch'], 'Working branch changed')
    if current == base:
        require(set(diff_paths(repo, 'diff', '--cached')) <= set(paths), 'Unrelated staged changes')
        for path, state in files.items():
            require(repo.file_state(path) == state, f'Reviewed worktree content changed: {path}')
        repo.git('--literal-pathspecs', 'add', '-A', '--', *paths)
        require(diff_paths(repo, 'diff', '--cached') == paths, 'Staged scope differs from review')
        verify_blobs(repo, ':', files)
        tree = repo.text('write-tree')
        login = actor['login']
        email = f"{actor['id']}+{login}@users.noreply.github.com"
        repo.git('-c', f'user.name={login}', '-c', f'user.email={email}', 'commit',
                 '--author', f'{login} <{email}>', '-m', f"Implement {contract['task_id']}")
        current = repo.text('rev-parse', 'HEAD')
        require(repo.text('rev-parse', f'{current}^{{tree}}') == tree,
                'Commit hooks or concurrent work changed the reviewed tree')
    require(repo.text('show', '-s', '--format=%P', current) == base
            and diff_paths(repo, 'diff-tree', '-r', '--no-commit-id', current) == paths,
            'Local commit does not match the authorized parent and paths')
    verify_blobs(repo, current, files)
    require(repo.text('show', '-s', '--format=%ae', current)
            == f"{actor['id']}+{actor['login']}@users.noreply.github.com", 'Commit author differs from GitHub actor')
    return current


def push_commit(repo, branch, head):
    # Use the same authenticated GitHub credential as the API. Keep it out of argv and output.
    require(re.fullmatch(r'(feature|fix|docs|test|chore)/\d+-[a-z0-9][a-z0-9-]*', branch)
            and re.fullmatch(r'[0-9a-f]{40}', head), 'Push requires an exact commit and numbered feature branch')
    require(repo.text('remote', 'get-url', '--push', '--all', 'origin') in HTTPS_URLS,
            'Canonical HTTPS push destination changed')
    token = base64.b64encode(('x-access-token:' + os.environ['GH_TOKEN']).encode()).decode()
    require('GIT_CONFIG_COUNT' not in os.environ and 'GIT_CONFIG_PARAMETERS' not in os.environ,
            'Unexpected command-scoped Git configuration')
    env = {key: value for key, value in os.environ.items()
           if not key.upper().startswith('GIT_TRACE')
           and key.upper() not in ('GIT_CURL_VERBOSE', 'GIT_SSL_NO_VERIFY')}
    env.update(GIT_CONFIG_COUNT='2', GIT_TERMINAL_PROMPT='0', GCM_INTERACTIVE='never',
               GIT_CONFIG_KEY_0='http.https://github.com/.extraHeader', GIT_CONFIG_VALUE_0='',
               GIT_CONFIG_KEY_1='http.https://github.com/.extraHeader',
               GIT_CONFIG_VALUE_1='Authorization: Basic ' + token)
    result = subprocess.run(['git', '-C', str(repo.root), '-c', 'credential.helper=', '-c', 'remote.origin.mirror=false',
                             '-c', 'http.followRedirects=false', '-c', 'http.sslVerify=true',
                             'push', '--no-follow-tags', '--recurse-submodules=no', 'origin',
                             f'{head}:refs/heads/{branch}'], env=env, capture_output=True, timeout=120)
    require(result.returncode == 0, f'Feature branch push failed (exit {result.returncode}); local commit preserved')


def find_pr(api, branch, issue, task_id, actor):
    query = urlencode(dict(head=f"{REPO.split('/')[0]}:{branch}", base='main', state='all'))
    matches = api.pages('/pulls?' + query)
    current = [pr for pr in matches if pr['state'] == 'open']
    merged = [pr for pr in matches if pr['state'] == 'closed'
              and api.call(f"/pulls/{pr['number']}").get('merged')]
    require(len(current + merged) <= 1, 'Multiple matching pull requests; reconciliation required')
    if not current and not merged:
        require(not matches, 'Previous pull request closed without merge; reconcile its disposition')
        # Refuse to create a competing PR for the same canonical task on a different branch.
        for pr in api.pages('/pulls?state=open&base=main'):
            require(not re.search(rf'^Task: #{issue}\s*$', pr.get('body') or '', re.M),
                    'An open pull request already claims this task')
        return None
    pr = api.call(f"/pulls/{(current + merged)[0]['number']}")
    require(pr['user']['login'].casefold() == actor.casefold()
            and pr['head']['repo']['full_name'] == REPO and pr['head']['ref'] == branch
            and pr['base']['repo']['full_name'] == REPO and pr['base']['ref'] == 'main'
            and re.findall(r'^Task: #(\d+)\s*$', pr.get('body') or '', re.M) == [str(issue)]
            and re.findall(r'^Plan: ([A-Z0-9-]+)\s*$', pr.get('body') or '', re.M) == [task_id],
            'Existing pull request does not match reviewed task, repository, branch and author')
    return pr


def ensure_pr(api, pr, contract, reviewed, issue, head):
    # Keep review-supplied text in a code block so it cannot add issue-closing keywords.
    summary = json.dumps({'acceptance_criteria': contract['acceptance_criteria'],
                          'checks': {name: check['status'] for name, check in reviewed['results'].items()}},
                         indent=2, ensure_ascii=True).replace(chr(96), '\\u0060')
    fence = chr(96) * 3
    report = quote(contract.get('report_path', 'report.md'), safe='/')
    body = (f"Task: #{issue}\nPlan: {contract['task_id']}\n\nCloses #{issue}\n\n"
            f"Review: {reviewed['review_id']}\n\n[Reviewed report](https://github.com/{REPO}/blob/{head}/{report})"
            f"\n\n{fence}json\n{summary}\n{fence}")
    if pr is None:
        pr = api.call('/pulls', 'POST', dict(title=f"Implement {contract['task_id']}", body=body,
                                            head=contract['branch'], base='main'))
    elif not re.fullmatch(re.escape(body) + r'(?:\n\nApproval evidence: [^\n]+)?', pr.get('body') or ''):
        require((pr.get('body') or '').strip() == f"Task: #{issue}\nPlan: {contract['task_id']}",
                'Existing PR contains independent content; reconcile its body before publication')
        pr = api.call(f"/pulls/{pr['number']}", 'PATCH', {'body': body})
    require(pr.get('head', {}).get('sha') == head and not pr.get('draft'), 'PR head or draft state is ineligible')
    return pr, body


def approve_and_trigger(api, pr, body, task, branch, head, actor, protected):
    number = pr['number']
    markers = [f'GENESIS-DEVELOPER-APPROVED: {task} {REPO} {branch} {head} merge']
    if protected:
        markers.append('GENESIS-OWNER-APPROVED: ' + head)
    comments = api.pages(f'/issues/{number}/comments')
    evidence = []
    for marker in markers:
        matches = [item for item in comments if gate.has_comment([item], actor, marker)]
        if not matches:
            matches = [api.call(f'/issues/{number}/comments', 'POST', {'body': marker})]
        require(all(gate.has_comment([item], actor, marker)
                    and re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', item.get('created_at', ''))
                    and re.fullmatch(rf'https://github\.com/{re.escape(REPO)}/pull/{number}#issuecomment-\d+',
                                     item.get('html_url', '')) for item in matches),
                'Authenticated approval evidence is incomplete')
        evidence.append(max(matches, key=lambda item: item['created_at']))
    approved_body = body + '\n\nApproval evidence: ' + ', '.join(item['html_url'] for item in evidence)
    # The trusted workflow listens to PR edits, not issue comments. Create a fresh run after approval.
    if pr['body'] != approved_body:
        updated = api.call(f'/pulls/{number}', 'PATCH', {'body': approved_body})
        require(updated['body'] == approved_body and updated['head']['sha'] == head,
                'PR changed while recording approval evidence')
    return max(item['created_at'] for item in evidence), approved_body


def check_state(api, sha, names, gate_after=None):
    runs = api.pages(f'/commits/{sha}/check-runs?filter=latest', key='check_runs')
    pending = []
    for name in sorted(names):
        matches = [run for run in runs if run['name'] == name and run.get('head_sha') == sha
                   and run.get('app', {}).get('slug') == 'github-actions'
                   and run['app'].get('id') == GITHUB_ACTIONS_APP
                   and (not gate_after or name not in TRUSTED_GATES or
                        (run.get('started_at') or '') >= gate_after)]
        require(not any(run['status'] == 'completed' and run['conclusion'] != 'success' for run in matches),
                f'Required check failed, skipped or cancelled: {name}')
        if not matches or any(run['status'] != 'completed' for run in matches):
            pending.append(name)
    return pending


def wait_checks(api, sha, names, *, gate_after, attempts=12, pause=time.sleep):
    for attempt in range(attempts):
        pending = check_state(api, sha, names, gate_after)
        if not pending:
            return []
        if attempt + 1 < attempts:
            pause(5)
    return pending


def post_merge(api, pr, task, plan, expected_head, expected_base, *, attempts, pause):
    number = pr['number']
    merged = api.call(f'/pulls/{number}')
    require(merged.get('merged') and merged['head']['sha'] == expected_head
            and merged['base']['repo']['full_name'] == REPO and merged['base']['ref'] == 'main',
            'Merged PR evidence does not match reviewed head and target')
    merge_sha = merged.get('merge_commit_sha') or ''
    require(re.fullmatch(r'[0-9a-f]{40}', merge_sha), 'Merge revision is unavailable')
    commit = api.call(f'/git/commits/{merge_sha}')
    require([parent['sha'] for parent in commit['parents']] == [expected_base, expected_head],
            'Merge parents differ from the verified base and head')
    main = ref(api, 'main')
    require(main, 'Live main is missing after merge')
    ancestry = api.call(f'/compare/{merge_sha}...{main}')
    require(ancestry.get('status') in ('ahead', 'identical')
            and ancestry.get('merge_base_commit', {}).get('sha') == merge_sha,
            'Merge commit is not reachable from main')
    pending = wait_checks(api, merge_sha, GOVERNANCE | {'pilot-checks'},
                          gate_after=None, attempts=attempts, pause=pause)
    record = dict(pr=number, head_sha=expected_head, ci_sha=expected_head, developer=merged['user']['login'],
                  evidence=[merged['html_url'], f'https://github.com/{REPO}/commit/{merge_sha}'])
    outcome = dict(status='MERGED_PENDING_ACCEPTANCE', pr=number, merge_sha=merge_sha,
                   handoff_record=record, rotation_written=False, phase_locked=False)
    if pending:
        return dict(outcome, pending_checks=pending)
    accepted = gate.policy_at(api, '.github/acceptance.json', main)['accepted']
    live_plan = gate.policy_at(api, '.github/task-plan.json', main)
    require(live_plan['repository'] == plan['repository'], 'Post-merge policy repository changed')
    try:
        proposal = gate.propose_handoff(merged, live_plan, accepted, record, api, main)
        require(ref(api, 'main') == main, 'Trusted main moved during acceptance verification')
    except Rejected as exc:
        return dict(outcome, blocker=str(exc))
    if proposal['status'] == 'ALREADY_ACCEPTED':
        return dict(outcome, status='ACCEPTED', handoff=proposal)
    comments = api.pages(f'/issues/{number}/comments')
    commits = api.pages(f'/pulls/{number}/commits')
    reviews = api.pages(f'/pulls/{number}/reviews')
    return dict(outcome, handoff=proposal, history=dict(
        task_id=task['plan_id'], assigned_owner=plan['sequential_execution']['active_owner'],
        pr_author=merged['user']['login'], actual_implementer=None,
        commit_authors=[(item.get('author') or {}).get('login') for item in commits],
        reviewers=[item['user']['login'] for item in reviews if item['state'] == 'APPROVED'
                   and item.get('commit_id') == expected_head],
        human_approver=record['developer'], approval_comments=[
            item['html_url'] for item in comments if (item.get('user') or {}).get('login') == record['developer']
            and (item.get('body') or '').startswith('GENESIS-DEVELOPER-APPROVED: ')
            and expected_head in item['body']
        ],
    ))


def observe_merge(repo, api, pr, task, plan, head, base_main, reported_sha, *, attempts, pause):
    try:
        result = post_merge(api, pr, task, plan, head, base_main, attempts=attempts, pause=pause)
    except (Rejected, RuntimeError, OSError, KeyError) as exc:
        return dict(status='MERGED_PENDING_ACCEPTANCE', pr=pr['number'], head=head,
                    reported_merge_sha=reported_sha, blocker=str(exc),
                    rotation_written=False, phase_locked=False)
    if result.get('handoff'):
        from lifecycle import State, clock, prepare_acceptance
        try:
            result['acceptance_transaction'] = prepare_acceptance(
                State(repo, api), pr['number'], head, base_main, clock())
        except (Rejected, RuntimeError, OSError, KeyError, TypeError, ValueError,
                subprocess.TimeoutExpired) as exc:
            result['acceptance_blocker'] = str(exc)
    return result


def publish(repo, api, contract, session, reviewed, approval, review_id, reference, journal, *,
            attempts=12, pause=time.sleep):
    require(approval == 'PUSHLA' and reference.strip(), 'Explicit PUSHLA authorization is required')
    require(contract['repository'] == REPO and contract['task_type'] == 'product',
            'Only ordinary product publication is supported; migration requires the separate bootstrap')
    require(repo.root == Path(repo.text('rev-parse', '--show-toplevel')).resolve(), 'Use the repository root')
    require(repo.text('remote', 'get-url', '--push', '--all', 'origin') in HTTPS_URLS,
            'Wrong or ambiguous canonical HTTPS push destination')
    local_main = repo.live_main()
    require(local_main == ref(api, 'main'), 'Git and GitHub main disagree')
    actor = api.identity()
    require(actor.get('type') == 'User' and type(actor.get('id')) is int
            and actor['login'].casefold() == contract['authorized_developer'].casefold(),
            'Authenticated GitHub developer differs from reviewed developer')
    info = api.call('/')
    require(info['full_name'] == REPO and info['default_branch'] == 'main'
            and info.get('permissions', {}).get('push') is True and info.get('allow_merge_commit') is True,
            'GitHub push permission or merge-commit support is unavailable')
    branch, base_main = contract['branch'], contract['source_main_sha']
    require(re.fullmatch(r'[0-9a-f]{40}', base_main) and contract['base_revision'] == base_main,
            'Ordinary publication requires a reviewed base equal to verified main')
    plan = json.loads(repo.blob(base_main, '.github/task-plan.json'))
    task = gate.validate_plan(plan).get(contract['task_id'])
    require(task and task['plan_id'] != 'F01-GOV'
            and re.fullmatch(rf"(feature|fix|docs|test|chore)/{task['issue_number']}-[a-z0-9][a-z0-9-]*", branch),
            'Invalid ordinary task publication branch')
    issue = task['issue_number']
    require(plan['repository'] == REPO and review_id == reviewed['review_id'], 'Wrong review or repository')
    journal = journal.resolve()
    require(not journal.is_relative_to(repo.root), 'Keep publication journal outside the checkout')
    binding = digest([contract, session, reviewed, actor['id'], reference])
    if journal.exists():
        recorded = json.loads(journal.read_bytes())
        require(recorded['binding'] == binding, 'Publication journal belongs to different reviewed work')
        files = recorded['files']
        require(sorted(files) == reviewed['changed_files'], 'Publication journal paths differ from review')
    else:
        require(local_main == base_main, 'Live main changed; refresh the review')
        trusted_activation(repo, base_main)
        active_protection(api)
        decide(repo, contract, session, reviewed, review_id, 'ONAYLA',
               contract['authorized_developer'], reference, api)
        current = repo.snapshot()
        require(digest(current) == reviewed['snapshot_id'], 'Worktree moved after approval validation')
        files = {path: current['changes'][path][1] for path in
                 path_list(reviewed['changed_files'], 'reviewed paths')}
        require(files.get(contract.get('report_path', 'report.md')), 'Reviewed task report is required')
        require(not diff_paths(repo, 'diff', '--cached'), 'Preserve existing staged changes before publication')
        require(not any(gate.protected_path(path) for path in files) or actor['login'].casefold() == OWNER,
                'Protected publication requires the separately authorized project owner as actor')
        with journal.open('x', encoding='utf-8') as output:
            json.dump(dict(binding=binding, files=files), output)

    pr = find_pr(api, branch, issue, task['plan_id'], actor['login'])
    if pr and pr.get('merged'):
        head = commit_reviewed(repo, contract, files, actor) if repo.text('rev-parse', 'HEAD') != contract[
            'base_revision'] else None
        require(head and pr['head']['sha'] == head, 'Merged PR does not match local publication commit')
        return observe_merge(repo, api, pr, task, plan, head, base_main, pr.get('merge_commit_sha'),
                             attempts=attempts, pause=pause)
    require(local_main == base_main, 'Live main changed; refresh the review')
    trusted_activation(repo, base_main)
    contexts, needs_review = active_protection(api)
    head = commit_reviewed(repo, contract, files, actor)
    remote_head = ref(api, branch)
    if remote_head != head:
        require(remote_head in (None, contract['base_revision']), 'Remote feature branch has unrelated commits')
        push_commit(repo, branch, head)
        require(ref(api, branch) == head, 'Published feature ref could not be verified')
    pr, body = ensure_pr(api, pr, contract, reviewed, issue, head)
    number = pr['number']
    gate_after, approved_body = approve_and_trigger(
        api, pr, body, task['plan_id'], branch, head, actor['login'],
        any(gate.protected_path(path) for path in files))
    names = contexts | gate.required_checks(task, [{'filename': path} for path in files])
    pending = wait_checks(api, head, names, gate_after=gate_after, attempts=attempts, pause=pause)
    if pending:
        return dict(status='PUBLISHED_PENDING_CI', pr=number, head=head, pending_checks=pending)
    require(not needs_review or api.review_decision(number) == 'APPROVED',
            'Required independent GitHub review is missing')
    pr = api.call(f'/pulls/{number}')
    require(pr['head']['sha'] == head and pr['body'] == approved_body
            and pr['base']['sha'] == base_main and ref(api, 'main') == base_main
            and ref(api, branch) == head and pr.get('mergeable') is True,
            'PR changed, became stale, or is not mergeable')
    accepted = json.loads(repo.blob(base_main, '.github/acceptance.json'))['accepted']
    gate.readiness(pr, plan, accepted, api)
    require(sorted(gate.changed_paths(api.pages(f'/pulls/{number}/files'))) == sorted(files),
            'Hosted diff paths differ from the reviewed change set')
    require(active_protection(api) == (contexts, needs_review)
            and not check_state(api, head, names, gate_after) and ref(api, 'main') == base_main,
            'Protection, CI or base changed before merge')
    result = api.call(f'/pulls/{number}/merge', 'PUT', {'sha': head, 'merge_method': 'merge'})
    require(result.get('merged') is True, 'GitHub declined the merge; published branch and PR preserved')
    return observe_merge(repo, api, pr, task, plan, head, base_main, result.get('sha'),
                         attempts=attempts, pause=pause)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('contract', 'session', 'review', 'journal'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--approval', required=True, choices=['PUSHLA'])
    parser.add_argument('--review-id', required=True)
    parser.add_argument('--approval-ref', required=True)
    args = parser.parse_args()
    try:
        repo = Repository()
        require(os.environ.get('GH_TOKEN'), 'Authenticated GitHub developer token is required')
        inputs = [args.contract, args.session, args.review, args.journal]
        require(all(not path.resolve().is_relative_to(repo.root) for path in inputs),
                'Keep review and publication records outside the checkout')
        contract, session, reviewed = (json.loads(path.read_bytes()) for path in inputs[:3])
        decision = args.session.with_name(f'{args.session.name}.{args.review_id}.decision.json')
        require(re.fullmatch(r'[0-9a-f]{64}', args.review_id), 'Invalid review identity')
        if decision.exists():
            require(json.loads(decision.read_bytes())['status'] == 'APPROVED_FOR_SEPARATE_PUBLICATION_REVIEW',
                    'The developer rejected or requested changes to this review')
        lock = decision.with_suffix('.publish.lock')
        with lock.open('x', encoding='utf-8'):
            pass
        try:
            result = publish(repo, GitHub(REPO, follow_redirects=False), contract, session, reviewed,
                             args.approval, args.review_id, args.approval_ref, args.journal)
        finally:
            lock.unlink()
        print(json.dumps(result, indent=2, ensure_ascii=True))
        return 0 if result['status'] == 'ACCEPTED' else 2
    except (Rejected, RuntimeError, OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as exc:
        parser.exit(1, f'PUBLICATION_BLOCKED: {exc}\n')


if __name__ == '__main__':
    raise SystemExit(main())
