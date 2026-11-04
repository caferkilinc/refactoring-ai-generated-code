"""Prepare protected Genesis records against a verified main, without publishing."""
import argparse
import json
import re
import subprocess
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

import gate
from gate import Rejected, require
from github_api import GitHub
from task_execution import REPO, REGISTRIES, Repository, digest
from repository_identity import effective_plan


PLAN, ACCEPTANCE = REGISTRIES
HISTORY = 'docs/history/GENESIS_EVENTS.jsonl'
OWNER = 'cakarburkayy'
MIGRATIONS = tuple(f'MIG-0{i}' for i in range(1, 6))
EVENT_TYPES = set('TASK_STARTED IMPLEMENTATION_VERIFIED DEVELOPER_APPROVED PR_MERGED '
                  'TASK_ACCEPTED ROTATION_ADVANCED PHASE_LOCKED PHASE_REOPENED '
                  'CORRECTION_RECORDED MIGRATION_ACCEPTED'.split())


def sha(value):
    return isinstance(value, str) and re.fullmatch(r'[a-f0-9]{40}', value) is not None


def clock():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def timestamp(value):
    try:
        return isinstance(value, str) and datetime.fromisoformat(value).tzinfo is not None
    except ValueError:
        return False


def https(value):
    parsed = urlsplit(value) if isinstance(value, str) else None
    return bool(parsed and parsed.scheme == 'https' and parsed.hostname and not parsed.username
                and not parsed.password and not any(char.isspace() for char in value))


def json_text(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + '\n'


def events_from(raw):
    require(not raw or raw.endswith(b'\n'), 'History must end with a newline')
    events = {}
    for line in raw.splitlines():
        entry = json.loads(line)
        require(isinstance(entry, dict) and entry['event_type'] in EVENT_TYPES
                and entry['subject_type'] in ('task', 'product_phase', 'migration_phase')
                and isinstance(entry['subject_id'], str) and bool(entry['subject_id'])
                and isinstance(entry['event_id'], str) and bool(entry['event_id'])
                and entry['event_id'] not in events and type(entry['backfilled']) is bool
                and 'actor_id' in entry and 'actor_role' in entry and 'pr' in entry
                and (entry['commit_sha'] is None or sha(entry['commit_sha']))
                and isinstance(entry['evidence'], list) and bool(entry['evidence'])
                and all(map(https, entry['evidence'])) and timestamp(entry['recorded_at'])
                and (entry['occurred_at'] is None or timestamp(entry['occurred_at'])),
                'Invalid or duplicate history event')
        if entry['event_type'] == 'CORRECTION_RECORDED':
            require(entry.get('previous_event') in events and entry.get('reason')
                    and entry['actor_id'] == OWNER and entry['actor_role'] == 'project_owner',
                    'Correction requires an existing event, reason and owner evidence')
        events[entry['event_id']] = entry
    return events


def append_events(raw, entries):
    existing = events_from(raw)
    additions = []
    for entry in entries:
        previous = existing.get(entry['event_id'])
        if previous:
            # The first recording time stays authoritative on retry.
            require(previous == dict(entry, recorded_at=previous['recorded_at']),
                    'Conflicting history event: ' + entry['event_id'])
            continue
        additions.append(json.dumps(entry, ensure_ascii=False, sort_keys=True) + '\n')
        existing[entry['event_id']] = entry
    result = raw.decode('utf-8') + ''.join(additions)
    events_from(result.encode('utf-8'))
    return result


def event(kind, domain, subject, key, revision, pr, evidence, recorded_at, *,
          actor=None, role=None, occurred_at=None, **details):
    return dict(event_id=f'{kind}:{domain}:{key}', event_type=kind, subject_type=domain,
                subject_id=subject, actor_id=actor, actor_role=role, commit_sha=revision, pr=pr,
                evidence=evidence, occurred_at=occurred_at, recorded_at=recorded_at,
                backfilled=False, **details)


def main_ref(repo, api):
    source = repo.live_main()
    hosted = api.call('/git/ref/heads/main')
    require(sha(source) and hosted['ref'] == 'refs/heads/main'
            and hosted['object']['type'] == 'commit' and hosted['object']['sha'] == source,
            'Git and GitHub main disagree')
    return source


class State:
    def __init__(self, repo, api, expected=None, *, activated=True):
        self.repo, self.api = repo, api
        self.main = main_ref(repo, api)
        require(expected is None or expected == self.main,
                'Trusted main moved; recompute against the updated source')
        try:
            repo.git('cat-file', '-e', self.main + '^{commit}')
        except Rejected:
            repo.git('-c', 'http.followRedirects=false', '-c', 'http.sslVerify=true',
                     '-c', 'fetch.prune=false', '-c', 'fetch.pruneTags=false', 'fetch',
                     '--no-prune', '--no-tags', '--no-recurse-submodules', '--no-write-fetch-head',
                     '--refmap=', 'origin', 'refs/heads/main')
            self.recheck()
            repo.git('cat-file', '-e', self.main + '^{commit}')
        if activated:
            from safe_publish import trusted_activation
            trusted_activation(repo, self.main)
            for name in ('lifecycle.py', 'next_step.py'):
                relative = 'scripts/governance/' + name
                require(repo.blob(self.main, relative) == Path(__file__).with_name(name).read_bytes(),
                        'Lifecycle implementation differs from trusted main: ' + relative)
        self.plan = effective_plan(json.loads(repo.blob(self.main, PLAN)), api, REPO)
        self.registry = json.loads(repo.blob(self.main, ACCEPTANCE))
        require(self.plan['repository'] == REPO and self.registry['schema_version'] == 1,
                'Unexpected trusted registry')
        self.tasks = gate.validate_plan(self.plan)
        self.accepted = self.registry['accepted']
        require(isinstance(self.accepted, dict)
                and set(self.accepted) <= {str(t['issue_number']) for t in self.tasks.values()},
                'Unknown acceptance issue')
        self.rotation = self.plan['sequential_execution']
        self.raw_history = (repo.blob(self.main, HISTORY) if repo.text('ls-tree', self.main, HISTORY)
                            else b'')
        self.events = events_from(self.raw_history)

    def recheck(self):
        require(main_ref(self.repo, self.api) == self.main,
                'Trusted main moved; recompute against the updated source')

    def record(self, task):
        return self.accepted.get(str(task['issue_number']))

    def reachable(self, revision):
        require(sha(revision), 'Missing merged revision')
        comparison = self.api.call(f'/compare/{revision}...{self.main}')
        require(comparison['status'] in ('ahead', 'identical')
                and comparison['merge_base_commit']['sha'] == revision,
                'Merge commit is not reachable from verified main')

    def verified_acceptance(self, task):
        record = self.record(task)
        pr = gate.verify_acceptance(task, record, self.api, self.plan)
        require(record.get('merge_sha', pr['merge_commit_sha']) == pr['merge_commit_sha'],
                'Canonical acceptance merge evidence conflicts')
        self.reachable(pr['merge_commit_sha'])
        return pr


def verify_checks(api, revision, names, gate_after=None):
    from safe_publish import check_state
    pending = check_state(api, revision, names, gate_after)
    require(not pending, 'Missing/failed required GitHub Actions checks: ' + ', '.join(pending))


def approval_marker(task, pr):
    head = pr['head']
    return f"GENESIS-DEVELOPER-APPROVED: {task['plan_id']} {REPO} {head['ref']} {head['sha']} merge"


def actor_comment(api, issue, login, marker):
    return next((comment for comment in api.pages(f'/issues/{issue}/comments')
                 if (comment.get('user') or {}).get('login', '').casefold() == login.casefold()
                 and (comment.get('body') or '').strip() == marker
                 and https(comment.get('html_url'))), None)


def select_next(state, completed, pr, explicit):
    accepted = {task['plan_id'] for task in state.tasks.values() if state.record(task)} | {completed}
    candidates = [task for task in state.tasks.values()
                  if task['plan_id'] not in accepted | {'F01-GOV'}
                  and set(task['dependencies']) <= accepted]
    if explicit is None:
        candidates = [task for task in candidates
                      if state.api.call(f"/issues/{task['issue_number']}")['state'] == 'open']
        require(len(candidates) == 1, 'Task selection needs a trusted decision. Eligible open tasks: '
                + ', '.join(sorted(task['plan_id'] for task in candidates)))
        return candidates[0]
    task = next((task for task in candidates if task['plan_id'] == explicit), None)
    require(task and state.api.call(f"/issues/{task['issue_number']}")['state'] == 'open',
            'Selected next task is ineligible')
    marker = f"GENESIS-NEXT-TASK: {REPO} {state.main} {pr['head']['sha']} {explicit}"
    require(actor_comment(state.api, pr['number'], OWNER, marker),
            'Explicit next task requires the project owner selection on the merged PR')
    return task


def prepare_acceptance(state, number, head, base, recorded_at, next_id=None):
    """Return all three record edits as one proposal. No Git refs or registries are written."""
    from safe_publish import GOVERNANCE, active_protection

    require(type(number) is int and number > 0 and sha(head) and sha(base)
            and timestamp(recorded_at), 'Invalid acceptance identity')
    api = state.api
    pr = api.call(f'/pulls/{number}')
    require(pr['number'] == number and pr['head']['sha'] == head,
            'Acceptance PR or source revision changed')
    task = gate.linked_task(pr, state.plan)
    existing = state.record(task)
    if existing is not None:
        require(existing['pr'] == number and existing['head_sha'] == head,
                'Conflicting canonical acceptance')
        merged = state.verified_acceptance(task)
        parents = api.call(f"/git/commits/{merged['merge_commit_sha']}")['parents']
        require([parent['sha'] for parent in parents] == [base, head],
                'Existing acceptance merge parents conflict')
        evaluation = evaluate_after_acceptance(state, task)
        state.recheck()
        return dict(status='ALREADY_ACCEPTED', source_main_sha=state.main, files={},
                    phase_evaluation=evaluation)

    developer = state.rotation['active_owner']
    revision = pr.get('merge_commit_sha')
    require(pr.get('merged') is True and sha(revision) and timestamp(pr.get('merged_at'))
            and https(pr.get('html_url')), 'PR merge evidence is unavailable')
    commit = api.call(f'/git/commits/{revision}')
    require([parent['sha'] for parent in commit['parents']] == [base, head],
            'Merge parents differ from the verified base and head')
    approval = actor_comment(api, number, developer, approval_marker(task, pr))
    edited = approval and (approval.get('updated_at') or approval.get('created_at'))
    require(approval and timestamp(approval.get('created_at')) and timestamp(edited)
            and datetime.fromisoformat(edited) <= datetime.fromisoformat(pr['merged_at']),
            'Missing pre-merge developer approval')
    record = dict(pr=number, head_sha=head, ci_sha=head, merge_sha=revision, developer=developer,
                  evidence=[pr['html_url'], f'https://github.com/{REPO}/commit/{revision}',
                            approval['html_url'], f'https://github.com/{REPO}/commit/{head}/checks',
                            f'https://github.com/{REPO}/commit/{revision}/checks'])
    proposal = gate.propose_handoff(pr, state.plan, state.accepted, record, api, state.main)
    files = api.pages(f'/pulls/{number}/files')
    contexts, needs_review = active_protection(api)
    verify_checks(api, head, contexts | gate.required_checks(task, files), edited)
    require(not needs_review or api.review_decision(number) == 'APPROVED',
            'Required independent GitHub review is missing')
    verify_checks(api, revision, GOVERNANCE | {'pilot-checks'})
    following = select_next(state, task['plan_id'], pr, next_id)
    # Validate the registered native edges now. The just-completed task has already
    # passed the handoff gate, while earlier prerequisites still need trusted records.
    accepted = deepcopy(state.registry)
    accepted['accepted'][str(task['issue_number'])] = record
    gate.check_dependencies(following, state.tasks, accepted['accepted'], api, state.plan)
    plan = deepcopy(state.plan)
    rotation = plan['sequential_execution']
    index = proposal['proposed_index']
    rotation.update(rotation_index=index, active_owner=proposal['proposed_owner'],
                    active_task_plan_id=following['plan_id'], handoff_confirmed=False,
                    last_accepted_handoff_key=proposal['handoff_key'],
                    last_confirmed_task_id=task['plan_id'], last_confirmed_commit=revision,
                    next_owner_if_accepted=rotation['team_sequence'][(index + 1) % len(rotation['team_sequence'])])
    rotation['note'] = (f"{task['plan_id']} accepted at {revision} via PR #{number}. "
                        f"{following['plan_id']} requires its own execution authorization.")
    gate.validate_plan(plan)
    key = proposal['handoff_key']
    contributors = dict(assigned_owner=developer, actual_implementer=None, pr_author=pr['user']['login'],
                        commit_authors=[dict(login=(item.get('author') or {}).get('login'),
                                             name=(item.get('commit', {}).get('author') or {}).get('name'))
                                        for item in api.pages(f'/pulls/{number}/commits')],
                        reviewer=sorted({item['user']['login'] for item in api.pages(f'/pulls/{number}/reviews')
                                         if item['state'] == 'APPROVED' and item.get('commit_id') == head
                                         and item['user']['login'].casefold() != developer.casefold()}) or None,
                        human_approver=developer)
    entries = [
        event('DEVELOPER_APPROVED', 'task', task['plan_id'], key, head, number, [approval['html_url']],
              recorded_at, actor=developer, role='authorized_developer', occurred_at=approval['created_at']),
        event('PR_MERGED', 'task', task['plan_id'], key, revision, number, record['evidence'], recorded_at,
              actor=(pr.get('merged_by') or {}).get('login'), role='github_merge_actor',
              occurred_at=pr['merged_at'], contributors=contributors),
        event('TASK_ACCEPTED', 'task', task['plan_id'], key, revision, number, record['evidence'], recorded_at,
              head_sha=head, contributors=contributors),
        event('ROTATION_ADVANCED', 'task', task['plan_id'], key, revision, number, record['evidence'],
              recorded_at, prior_index=state.rotation['rotation_index'], next_index=index,
              next_owner=rotation['active_owner'], next_task=following['plan_id']),
    ]
    output = {ACCEPTANCE: json_text(accepted), PLAN: json_text(plan),
              HISTORY: append_events(state.raw_history, entries)}
    state.recheck()
    return dict(status='MERGED_PENDING_ACCEPTANCE', source_main_sha=state.main, handoff_key=key,
                requires='INDEPENDENT_PROTECTED_RECORD_REVIEW_AND_INTEGRATION',
                transaction_id=digest([REPO, state.main, output]), files=output,
                phase_evaluation=dict(phase_id=task['phase'], status='AWAITING_CANONICAL_ACCEPTANCE'))


def phase_records(events):
    phases = {}
    for entry in events.values():
        kind, domain, phase = (entry[key] for key in ('event_type', 'subject_type', 'subject_id'))
        if kind not in ('MIGRATION_ACCEPTED', 'PHASE_LOCKED', 'PHASE_REOPENED'):
            continue
        require(domain in ('product_phase', 'migration_phase')
                and ((phase in MIGRATIONS) == (domain == 'migration_phase'))
                and entry['actor_id'] == OWNER and entry['actor_role'] == 'project_owner'
                and sha(entry['commit_sha']), 'Invalid phase authority or identity')
        current = phases.setdefault(phase, {})
        if kind == 'MIGRATION_ACCEPTED':
            require(domain == 'migration_phase' and 'acceptance' not in current,
                    'Duplicate or invalid migration acceptance')
            current['acceptance'] = entry
        elif kind == 'PHASE_LOCKED':
            require(current.get('status') != 'LOCKED'
                    and entry.get('previous_event') == current.get('event_id')
                    and (domain != 'migration_phase' or 'acceptance' in current),
                    'Conflicting phase lock')
            current.update(status='LOCKED', event_id=entry['event_id'], lock=entry)
        else:
            require(current.get('status') == 'LOCKED' and entry.get('reason')
                    and entry.get('previous_event') == current['event_id'], 'Invalid phase reopening')
            current.update(status='REOPENED', event_id=entry['event_id'])
    return phases


def phase_tasks(state, phase):
    return [task for task in state.tasks.values() if task['phase'] == phase]


def phase_evidence(state, phase):
    from safe_publish import GOVERNANCE

    if phase in MIGRATIONS:
        records = phase_records(state.events)
        required = MIGRATIONS[:MIGRATIONS.index(phase) + 1]
        require(all(records.get(key, {}).get('acceptance') for key in required),
                'Missing trusted migration acceptance')
        acceptance = records[phase]['acceptance']
        state.reachable(acceptance['commit_sha'])
        verify_checks(state.api, state.main, GOVERNANCE | {'pilot-checks'})
        return [phase], [], acceptance['evidence']
    tasks = phase_tasks(state, phase)
    require(tasks, 'Unknown product phase')
    missing = [task['plan_id'] for task in tasks if not state.record(task)]
    require(not missing, 'Incomplete phase: ' + ', '.join(missing))
    links, owners = set(), set()
    for task in tasks:
        pr = state.verified_acceptance(task)
        gate.check_dependencies(task, state.tasks, state.accepted, state.api, state.plan)
        record = state.record(task)
        if record.get('developer'):
            owners.add(record['developer'])
        links.update(record['evidence'])
        require(https(pr['html_url']), 'Missing phase PR evidence')
    verify_checks(state.api, state.main, GOVERNANCE | {'pilot-checks'})
    return [task['plan_id'] for task in tasks], sorted(owners), sorted(links)


def evaluate_after_acceptance(state, task):
    phase = task['phase']
    if phase_records(state.events).get(phase, {}).get('status') == 'LOCKED':
        return dict(phase_id=phase, status='LOCKED')
    try:
        phase_evidence(state, phase)
    except (Rejected, RuntimeError) as exc:
        return dict(phase_id=phase, status='BLOCKED', reason=str(exc))
    return dict(phase_id=phase, status='ELIGIBLE_PENDING_OWNER_LOCK_RECORD')


def prepare_phase(state, action, phase, evidence, reason, recorded_at, pr_number=None):
    """Prepare one owner-authorized phase event against trusted records."""
    from safe_publish import GOVERNANCE, active_protection

    require(action in ('lock', 'reopen', 'migration-accept') and timestamp(recorded_at)
            and https(evidence), 'Invalid phase request or evidence')
    migration = phase in MIGRATIONS
    tasks = phase_tasks(state, phase)
    require(migration or tasks, 'Unknown phase')
    domain = 'migration_phase' if migration else 'product_phase'
    current = phase_records(state.events).get(phase, {})
    previous = current.get('event_id')
    if action == 'lock' and current.get('status') == 'LOCKED':
        lock = current['lock']
        require(evidence == lock['verification_evidence'], 'Conflicting evidence for an existing phase lock')
        state.recheck()
        return dict(status='ALREADY_LOCKED', source_main_sha=state.main, files={})
    if action == 'reopen':
        require(current.get('status') == 'LOCKED' and reason and reason.strip(),
                'Reopening requires a current lock and a correction reason')
    require(action == 'migration-accept' or pr_number is None, 'Unexpected migration PR')
    contexts, needs_review = active_protection(state.api)
    anchor = 1 if migration else tasks[0]['issue_number']
    decision_id = digest([REPO, state.main, action, phase, evidence, reason, previous, pr_number])
    marker = f'GENESIS-PHASE-DECISION: {REPO} {decision_id}'
    decision = actor_comment(state.api, anchor, OWNER, marker)
    require(decision, f'Missing exact project owner decision on issue #{anchor}: {marker}')
    authority = decision['html_url']
    key = f'{phase}:{digest(previous)}'
    decided_at = decision.get('updated_at') or decision.get('created_at')
    require(timestamp(decided_at), 'Missing project owner decision time')
    common = dict(actor=OWNER, role='project_owner', occurred_at=decided_at)
    if action == 'migration-accept':
        require(migration and type(pr_number) is int and pr_number > 0 and 'acceptance' not in current,
                'Invalid or duplicate migration acceptance')
        pr = state.api.call(f'/pulls/{pr_number}')
        head, merge = pr['head']['sha'], pr['merge_commit_sha']
        require(pr['number'] == pr_number and pr.get('merged') is True and sha(head) and sha(merge)
                and pr['head']['ref'] == 'chore/1-genesis-v3-phase1'
                and pr['head']['repo']['full_name'] == REPO
                and pr['base']['repo']['full_name'] == REPO and pr['base']['ref'] == 'main'
                and https(pr.get('html_url')), 'Migration PR identity is not verified')
        state.reachable(merge)
        require(all(phase_records(state.events).get(prior, {}).get('acceptance')
                    for prior in MIGRATIONS[:MIGRATIONS.index(phase)]),
                'Earlier migration acceptance is missing from trusted main')
        parents = state.api.call(f'/git/commits/{merge}')['parents']
        require(len(parents) == 2 and parents[1]['sha'] == head and sha(parents[0]['sha']),
                'Migration merge head is unverified')
        verify_checks(state.api, head, contexts)
        require(not needs_review or state.api.review_decision(pr_number) == 'APPROVED',
                'Required independent migration review is missing')
        verify_checks(state.api, merge, GOVERNANCE | {'pilot-checks'})
        entry = event('MIGRATION_ACCEPTED', domain, phase, key, merge, pr_number,
                      [evidence, authority, pr['html_url']], recorded_at, head_sha=head, **common)
    elif action == 'lock':
        accepted, contributors, links = phase_evidence(state, phase)
        entry = event('PHASE_LOCKED', domain, phase, key, state.main, None,
                      [evidence, authority, *links], recorded_at, **common, status='LOCKED',
                      phase_id=phase, phase_type=domain, previous_event=previous, lock_revision=state.main,
                      accepted_tasks=accepted, contributors=contributors or None,
                      verification_evidence=evidence, locking_authority=authority, locked_at=decided_at)
    else:
        entry = event('PHASE_REOPENED', domain, phase, key, state.main, None,
                      [evidence, authority], recorded_at, **common, previous_event=previous, reason=reason)
    history = append_events(state.raw_history, [entry])
    phase_records(events_from(history.encode('utf-8')))
    state.recheck()
    files = {HISTORY: history}
    return dict(status='PHASE_RECORD_PENDING_INTEGRATION', source_main_sha=state.main,
                transaction_id=digest([REPO, state.main, files]), files=files)


def prepare_correction(state, target, reason, evidence, recorded_at):
    previous = state.events.get(target)
    require(previous and isinstance(reason, str) and reason.strip() and https(evidence)
            and timestamp(recorded_at), 'Correction requires an existing event, reason and HTTPS evidence')
    domain, subject = previous['subject_type'], previous['subject_id']
    key = digest([target, reason, evidence])
    if f'CORRECTION_RECORDED:{domain}:{key}' in state.events:
        state.recheck()
        return dict(status='ALREADY_RECORDED', source_main_sha=state.main, files={})
    if domain == 'task':
        anchor = state.tasks[subject]['issue_number']
    else:
        anchor = 1 if domain == 'migration_phase' else phase_tasks(state, subject)[0]['issue_number']
    marker = f'GENESIS-HISTORY-CORRECTION: {REPO} {state.main} {key}'
    decision = actor_comment(state.api, anchor, OWNER, marker)
    require(decision, f'Missing exact owner correction decision on issue #{anchor}: {marker}')
    decided_at = decision.get('updated_at') or decision.get('created_at')
    require(timestamp(decided_at), 'Missing project owner decision time')
    entry = event('CORRECTION_RECORDED', domain, subject, key, state.main, previous['pr'],
                  [evidence, decision['html_url']], recorded_at, actor=OWNER, role='project_owner',
                  occurred_at=decided_at, previous_event=target, reason=reason)
    files = {HISTORY: append_events(state.raw_history, [entry])}
    state.recheck()
    return dict(status='HISTORY_CORRECTION_PENDING_INTEGRATION', source_main_sha=state.main,
                transaction_id=digest([REPO, state.main, files]), files=files)


def verify_candidate(state, proposal, candidate):
    """Verify the exact single-commit proposal before its separately authorized PR."""
    files = proposal['files']
    require(sha(candidate) and files and proposal['source_main_sha'] == state.main,
            'Missing candidate or stale proposal')
    require(state.repo.text('rev-list', '--parents', '-n', '1', candidate).split()
            == [candidate, state.main], 'Candidate must be one commit on the verified transaction base')
    paths = state.repo.git('diff', '--name-only', '-z', '--no-renames', state.main, candidate)
    require(set(paths.decode().split('\0')[:-1]) == set(files), 'Candidate contains a different path set')
    for path, content in files.items():
        require(state.repo.text('ls-tree', candidate, path).startswith('100644 blob ')
                and state.repo.blob(candidate, path) == content.encode('utf-8'),
                'Candidate differs from reviewed transaction: ' + path)
    state.recheck()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--expected-main', required=True)
    parser.add_argument('--recorded-at', required=True, help='Time of the reviewed proposal, retained on retry')
    parser.add_argument('--verify', type=Path, help='Recompute and compare the exact reviewed proposal')
    parser.add_argument('--candidate', help='Verify the prepared single-commit candidate by full SHA')
    sub = parser.add_subparsers(dest='action', required=True)
    accept = sub.add_parser('accept')
    accept.add_argument('--pr', required=True, type=int)
    accept.add_argument('--head', required=True)
    accept.add_argument('--base', required=True)
    accept.add_argument('--next-task')
    phase = sub.add_parser('phase')
    phase.add_argument('operation', choices=['lock', 'reopen', 'migration-accept'])
    phase.add_argument('phase_id')
    phase.add_argument('--evidence', required=True)
    phase.add_argument('--reason')
    phase.add_argument('--pr', type=int)
    correct = sub.add_parser('correct')
    correct.add_argument('--event', required=True)
    correct.add_argument('--reason', required=True)
    correct.add_argument('--evidence', required=True)
    args = parser.parse_args()
    try:
        repo = Repository()
        api = GitHub(REPO, follow_redirects=False)
        state = State(repo, api, args.expected_main)
        if args.action == 'accept':
            result = prepare_acceptance(state, args.pr, args.head, args.base,
                                        args.recorded_at, args.next_task)
        elif args.action == 'phase':
            result = prepare_phase(state, args.operation, args.phase_id, args.evidence, args.reason,
                                   args.recorded_at, args.pr)
        else:
            result = prepare_correction(state, args.event, args.reason, args.evidence, args.recorded_at)
        if args.verify:
            require(json.loads(args.verify.read_bytes()) == result,
                    'Reviewed transaction differs from the verified proposal')
        if args.candidate:
            require(args.verify, 'Candidate verification requires the exact reviewed proposal')
            verify_candidate(state, result, args.candidate)
        print(json.dumps(result, ensure_ascii=True, indent=2))
    except (Rejected, RuntimeError, OSError, KeyError, ValueError, TypeError,
            subprocess.TimeoutExpired) as exc:
        parser.exit(1, f'LIFECYCLE_BLOCKED: {exc}\n')


if __name__ == '__main__':
    main()
