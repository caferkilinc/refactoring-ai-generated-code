"""Read-only Git guards and local review evidence for one authorized Genesis task."""
import argparse
import hashlib
import json
import os
import platform
import re
import stat
import subprocess
from pathlib import Path

from gate import (Rejected, check_dependencies, check_paths, protected_path, require,
                  required_checks, validate_plan)
from github_api import GitHub
from repository_identity import current_repository, effective_plan, repository_urls


REPO = current_repository()
URLS = repository_urls(REPO)
REGISTRIES = ('.github/task-plan.json', '.github/acceptance.json')
CONTEXT = ('AGENTS.md', *REGISTRIES)
FROZEN = ('experiments/original-ai-code/', 'experiments/java-pilot/manifests/',
          'experiments/java-pilot/provenance/', 'tests/fixtures/',
          'docs/history/genesis_events.jsonl', *REGISTRIES)
MIGRATION_PATHS = (
    '.agents/skills/task-execution/', '.agents/skills/development-handoff/SKILL.md',
    'scripts/governance/task_execution.py', 'tests/governance/test_task_execution.py',
    'docs/reports/MIG-03.md', 'docs/reports/MIG-03-ATTEMPT-1-BLOCKED.md',
)
MIGRATION_CHECKS = {'governance-tests', 'documentation-checks', 'security-checks'}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True).encode()).hexdigest()


def inside(path, scope):
    return any(path.startswith(item) if item.endswith('/') else path == item for item in scope)


def path_list(values, label, *, empty=False, prefixes=False):
    require(isinstance(values, list) and (values or empty), f'Missing {label}')
    for value in values:
        require(isinstance(value, str) and value and not re.search(r'[\\:\x00-\x1f]', value),
                f'Invalid path in {label}')
        path = value.removesuffix('/') if prefixes else value
        require(all(part and part not in ('.', '..') and part.casefold() != '.git'
                    for part in path.split('/')), f'Unsafe path in {label}: {value}')
    require(len(values) == len(set(values)), f'Duplicate path in {label}')
    return values


class Repository:
    def __init__(self, root='.'):
        self.root = Path(root).resolve()

    def git(self, *args):
        env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', GIT_TERMINAL_PROMPT='0', GCM_INTERACTIVE='never')
        result = subprocess.run(['git', '-C', str(self.root), *args], env=env,
                                capture_output=True, timeout=45)
        require(result.returncode == 0, f'Git {args[0]} failed (exit {result.returncode})')
        return result.stdout

    def text(self, *args):
        return self.git(*args).decode('utf-8').strip()

    def live_main(self):
        require(self.text('remote', 'get-url', 'origin') in URLS
                and self.text('ls-remote', '--get-url', 'origin') in URLS,
                'Wrong canonical origin')
        line = self.text('-c', 'http.followRedirects=false', '-c', 'http.sslVerify=true',
                         'ls-remote', '--exit-code', '--refs', 'origin', 'refs/heads/main')
        match = re.fullmatch(r'([a-f0-9]{40})\s+refs/heads/main', line)
        require(match, 'Live main is unavailable or ambiguous')
        return match[1]

    def blob(self, sha, path):
        try:
            return self.git('show', f'{sha}:{path}')
        except Rejected:
            raise Rejected(f'Missing required source at {sha}: {path}') from None

    def file_state(self, name):
        path = self.root / name
        require(path.resolve().is_relative_to(self.root), f'Path escapes worktree: {name}')
        require(not any(part.is_symlink() or getattr(part, 'is_junction', lambda: False)()
                        for part in (path, *path.parents) if part != self.root and
                        part.is_relative_to(self.root)), f'Linked path requires separate review: {name}')
        if not path.exists():
            return None
        mode = path.stat().st_mode
        require(stat.S_ISREG(mode), f'Unsupported worktree entry: {name}')
        with path.open('rb') as file:
            return [stat.S_IMODE(mode), hashlib.file_digest(file, 'sha256').hexdigest()]

    def snapshot(self):
        for name in ('index.lock', 'MERGE_HEAD', 'CHERRY_PICK_HEAD', 'REVERT_HEAD',
                     'rebase-merge', 'rebase-apply', 'sequencer'):
            path = Path(self.text('rev-parse', '--git-path', name))
            require(not (self.root / path).exists(), f'Git operation in progress: {name}')
        paths = self.git('ls-files', '-v', '-z').decode().split('\0')[:-1]
        require(not any(row[0] != 'H' for row in paths), 'Unsupported index flags or unmerged files')
        protected = {row[2:]: self.file_state(row[2:]) for row in paths
                     if protected_path(row[2:]) or inside(row[2:], FROZEN)}
        rows = self.git('status', '--porcelain=v1', '-z', '--no-renames',
                        '--untracked-files=all', '--ignored=matching').decode().split('\0')[:-1]
        changes = {row[3:]: [row[:2], self.file_state(row[3:])]
                   for row in rows if not row.startswith('!! ')}
        return dict(changes=changes, ignored=sorted(row[3:] for row in rows if row.startswith('!! ')),
                    protected=protected, index=hashlib.sha256(self.git('ls-files', '--stage', '-z')).hexdigest())


def authorize(repo, contract, api=None):
    require(isinstance(contract, dict), 'Task contract must be an object')
    for field in ('repository', 'task_id', 'task_title', 'task_type', 'authorized_developer',
                  'branch', 'base_revision', 'source_main_sha', 'objective', 'authorization_reference'):
        require(isinstance(contract.get(field), str) and contract[field].strip(),
                f'Missing contract field: {field}')
    for field in ('acceptance_criteria', 'stop_conditions', 'prerequisites'):
        values = contract.get(field)
        require(isinstance(values, list) and (values or field == 'prerequisites')
                and all(isinstance(v, str) and v.strip() for v in values), f'Invalid {field}')
    commands = contract.get('verification_requirements')
    require(isinstance(commands, dict) and all(isinstance(key, str) and key.strip() for key in commands),
            'Invalid verification requirements')
    for name, argv in commands.items():
        require(argv is None or (isinstance(argv, list) and argv
                                and all(isinstance(arg, str) and arg for arg in argv)),
                f'Invalid command for {name}')
        require(not argv or not any(Path(arg).name in ('task_execution', 'task_execution.py') for arg in argv),
                f'Recursive execution command for {name}')
    require(contract['repository'] == REPO and repo.root == Path(repo.text(
        'rev-parse', '--show-toplevel')).resolve(), 'Invalid repository or checkout root')
    main = repo.live_main()
    require(main == contract['source_main_sha'], 'Stale canonical main revision')
    require(repo.text('rev-parse', 'HEAD') == contract['base_revision']
            and repo.text('branch', '--show-current') == contract['branch'],
            'Wrong working branch or base revision')
    repo.git('merge-base', '--is-ancestor', main, contract['base_revision'])
    for path in set(CONTEXT) | set(path_list(contract.get('required_context'), 'required_context')):
        repo.blob(main, path)
    plan, accepted = (json.loads(repo.blob(main, path)) for path in REGISTRIES)
    plan = effective_plan(plan, api, REPO)
    require(plan['repository'] == REPO, 'Registry repository mismatch')
    ids = validate_plan(plan)
    scopes = path_list(contract.get('allowed_paths'), 'allowed_paths', prefixes=True)
    path_list(contract.get('protected_paths'), 'protected_paths', empty=True, prefixes=True)
    path_list(contract.get('existing_changes', []), 'existing_changes', empty=True)
    grant = contract.get('protected_authorization')
    if grant is not None:
        require(isinstance(grant, dict) and isinstance(grant.get('reference'), str)
                and grant['reference'].strip(), 'Missing separate protected authorization reference')
        require(all(grant.get(field) == contract[field] for field in
                    ('repository', 'task_id', 'authorized_developer', 'branch', 'base_revision')),
                'Protected authorization scope does not match contract')
        for path in path_list(grant.get('paths'), 'protected authorization paths'):
            require(inside(path, scopes) and not inside(path.casefold(), FROZEN),
                    f'Protected authorization cannot cover {path}')
    for path in scopes:
        require(not inside(path.casefold(), FROZEN) and not inside(path, contract['protected_paths']),
                f'Immutable or excluded scope: {path}')
        if protected_path(path) and not path.endswith('/'):
            require(grant and path in grant['paths'], f'Protected authorization required: {path}')

    if contract['task_type'] == 'migration':
        require(contract['task_id'] == 'MIG-03' and not contract['prerequisites'],
                'Unsupported migration contract')
        require(grant, 'Separate protected migration authorization required')
        require(all(inside(path, MIGRATION_PATHS) for path in scopes), 'Unauthorized migration scope')
        for name in ('repo-bootstrap', 'task-context', 'verification', 'development-handoff'):
            require(repo.file_state(f'.agents/skills/{name}/SKILL.md'),
                    f'Missing MIG-02 prerequisite: {name}')
        return None
    require(contract['task_type'] == 'product', 'Unknown task type')
    task = ids.get(contract['task_id'])
    require(task, 'Unknown registered product task')
    rotation = plan['sequential_execution']
    require(task['plan_id'] == rotation['active_task_plan_id']
            and contract['authorized_developer'] == rotation['active_owner'],
            'Wrong active task or developer')
    require(sorted(contract['prerequisites']) == sorted(task['dependencies']), 'Prerequisite scope mismatch')
    require(str(task['issue_number']) not in accepted['accepted'], 'Task already accepted')
    for path in scopes:
        check_paths(task, [{'filename': path}])
    require(api is not None, 'Read-only GitHub evidence is required for product authorization')
    issue = api.call(f"/issues/{task['issue_number']}")
    require(issue.get('state') == 'open' and 'pull_request' not in issue, 'Product issue is not open')
    check_dependencies(task, ids, accepted['accepted'], api, plan)
    return task


def start(repo, contract, api=None):
    authorize(repo, contract, api)
    initial = repo.snapshot()
    require(set(initial['changes']) == set(contract.get('existing_changes', [])),
            'Unexpected starting changes; record their provenance before starting')
    return dict(status='TASK_AUTHORIZED', contract_id=digest(contract), initial=initial)


def inspect_scope(contract, session, current, task):
    require(session['status'] == 'TASK_AUTHORIZED' and session['contract_id'] == digest(contract),
            'Session does not match authorized contract')
    initial = session['initial']
    require(current['index'] == initial['index'], 'Index changed during execution')
    require(current['ignored'] == initial['ignored'], 'Ignored output inventory changed')
    for path, state in initial['changes'].items():
        require(current['changes'].get(path) == state, f'Existing developer work changed: {path}')
    changes = {path: state for path, state in current['changes'].items()
               if path not in initial['changes']}
    for path in initial['protected'].keys() | current['protected'].keys():
        if initial['protected'].get(path) != current['protected'].get(path):
            require(path in changes, f'Protected bytes changed outside reported diff: {path}')
    path_list(list(changes), 'review paths')
    grant = contract.get('protected_authorization') or {}
    for path in changes:
        require(not inside(path.casefold(), FROZEN)
                and not inside(path, contract['protected_paths']), f'Protected path changed: {path}')
        require(inside(path, contract['allowed_paths']), f'Out-of-task path: {path}')
        require(not protected_path(path) or path in grant.get('paths', []),
                f'Protected authorization required: {path}')
    if task:
        check_paths(task, [{'filename': path} for path in changes])
    return changes


def run_checks(repo, contract, mandatory):
    commands = contract['verification_requirements']
    env = {key: value for key, value in os.environ.items() if key not in ('GH_TOKEN', 'GITHUB_TOKEN')}
    results = {}
    for name in sorted(mandatory | commands.keys()):
        argv = commands.get(name)
        result = dict(check_id=name, command=argv, status='NOT_RUN', exit_code=None,
                      environment=platform.platform(), source_revision=contract['base_revision'],
                      evidence='No executable check was supplied')
        if argv:
            try:
                process = subprocess.run(argv, cwd=repo.root, env=env, shell=False, timeout=600,
                                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                result.update(status='PASS' if process.returncode == 0 else 'FAIL',
                              exit_code=process.returncode, evidence='Local subprocess exit code')
            except (OSError, subprocess.TimeoutExpired):
                result.update(status='BLOCKED', evidence='Command unavailable or exceeded its timeout')
        results[name] = result
    return results


def review(repo, contract, session, api=None):
    task = authorize(repo, contract, api)
    current = repo.snapshot()
    changes = inspect_scope(contract, session, current, task)
    mandatory = required_checks(task, [{'filename': path} for path in changes]) if task else MIGRATION_CHECKS
    results = run_checks(repo, contract, mandatory)
    require(repo.snapshot() == current, 'Verification changed the review snapshot')
    require(repo.text('rev-parse', 'HEAD') == contract['base_revision']
            and repo.text('branch', '--show-current') == contract['branch']
            and repo.live_main() == contract['source_main_sha'], 'Source moved during verification')
    ready = all(result['status'] == 'PASS' for result in results.values())
    record = dict(status='HUMAN_APPROVAL_PENDING' if ready else 'BLOCKED',
                  states=['LOCAL_VERIFIED', 'REVIEW_REQUIRED', 'HUMAN_APPROVAL_PENDING'] if ready else ['BLOCKED'],
                  contract_id=digest(contract), session_id=digest(session), snapshot_id=digest(current),
                  task_id=contract['task_id'], developer=contract['authorized_developer'],
                  repository=contract['repository'], source_main_sha=contract['source_main_sha'],
                  branch=contract['branch'], head=contract['base_revision'], changed_files=sorted(changes),
                  results=results, publication_authorized=False)
    return dict(record, review_id=digest(record))


def decide(repo, contract, session, reviewed, review_id, choice, developer, reference, api=None):
    require(developer == contract['authorized_developer'] and reference.strip(),
            'Explicit developer decision and evidence reference required')
    require(choice in ('ONAYLA', 'DÜZELT', 'REDDET'), 'Unknown developer decision')
    record = {key: value for key, value in reviewed.items() if key != 'review_id'}
    require(reviewed['review_id'] == review_id == digest(record) and record['contract_id'] == digest(contract)
            and record['session_id'] == digest(session), 'Review record does not match this task session')
    decision = dict(review_id=review_id, developer=developer, approval_reference=reference,
                    publication_authorized=False)
    if choice != 'ONAYLA':
        return dict(status='CORRECTION_REQUIRED' if choice == 'DÜZELT' else 'REJECTED',
                    **decision)
    task = authorize(repo, contract, api)
    current = repo.snapshot()
    changes = inspect_scope(contract, session, current, task)
    mandatory = required_checks(task, [{'filename': path} for path in changes]) if task else MIGRATION_CHECKS
    require(record['status'] == 'HUMAN_APPROVAL_PENDING'
            and (mandatory | contract['verification_requirements'].keys()) == record['results'].keys()
            and all(result['status'] == 'PASS' and result['exit_code'] == 0
                    for result in record['results'].values()), 'Mandatory verification has not passed')
    require(record['snapshot_id'] == digest(current) and record['changed_files'] == sorted(changes),
            'Stale approval: reviewed content changed')
    return dict(status='APPROVED_FOR_SEPARATE_PUBLICATION_REVIEW', **decision)


def record_decision(repo, session_file, reviewed, result):
    """Keep one terminal choice per review in the private local session directory."""
    session_file = session_file.resolve()
    require(not session_file.is_relative_to(repo.root), 'Store decision evidence outside the checkout')
    receipt = session_file.with_name(f"{session_file.name}.{reviewed['review_id']}.decision.json")
    try:
        with receipt.open('x', encoding='utf-8') as output:
            json.dump(result, output, ensure_ascii=True, indent=2)
    except FileExistsError:
        raise Rejected('A decision for this review already exists; prepare a fresh review') from None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('start', 'review', 'decision'))
    parser.add_argument('--contract', type=Path, required=True)
    parser.add_argument('--session', type=Path)
    parser.add_argument('--review', type=Path)
    parser.add_argument('--review-id')
    parser.add_argument('--choice', choices=('ONAYLA', 'DÜZELT', 'REDDET'))
    parser.add_argument('--developer')
    parser.add_argument('--approval-ref')
    args = parser.parse_args()
    try:
        repo = Repository()
        contract = json.loads(args.contract.read_text(encoding='utf-8'))
        api = GitHub(REPO) if os.environ.get('GH_TOKEN') else None
        if args.mode == 'start':
            result = start(repo, contract, api)
        else:
            require(args.session, 'Supply the original --session record')
            session = json.loads(args.session.read_text(encoding='utf-8'))
            if args.mode == 'review':
                result = review(repo, contract, session, api)
            else:
                require(args.review and args.review_id and args.choice and args.developer and args.approval_ref,
                        'Supply review, exact review ID, decision, developer and approval evidence')
                reviewed = json.loads(args.review.read_text(encoding='utf-8'))
                result = decide(repo, contract, session, reviewed, args.review_id, args.choice,
                                args.developer, args.approval_ref, api)
                record_decision(repo, args.session, reviewed, result)
        print(json.dumps(result, ensure_ascii=True, indent=2))
        return int(result['status'] in ('BLOCKED', 'REJECTED', 'CORRECTION_REQUIRED'))
    except (Rejected, OSError, ValueError, KeyError, TypeError, AttributeError,
            RuntimeError, subprocess.TimeoutExpired) as exc:
        parser.exit(1, f'{"AUTHORIZATION_BLOCKED" if args.mode == "start" else "BLOCKED"}: {exc}\n')


if __name__ == '__main__':
    raise SystemExit(main())
