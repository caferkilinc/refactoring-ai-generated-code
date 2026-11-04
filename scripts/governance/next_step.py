"""Derive status and draft one next task from verified, accepted Genesis state."""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import gate
from gate import Rejected, require
from github_api import GitHub
from lifecycle import ACCEPTANCE, HISTORY, MIGRATIONS, PLAN, State, https, phase_records, verify_checks
from safe_publish import active_protection
from task_execution import FROZEN, REPO


POLICY = 'docs/governance/PROJECT_GENESIS_CODEX_NATIVE_PROTOCOL_V3.md'
HANDOFF_INTENT = 'docs/governance/migrations/POST_MIGRATION_HANDOFF.json'
PRODUCT_DOCS = ('docs/SRS.md', 'docs/SRS_EN.md', 'docs/ARCHITECTURE.md')
SKILLS = ('.agents/skills/task-execution/SKILL.md', '.agents/skills/verification/SKILL.md',
          '.agents/skills/safe-publish/SKILL.md')
COMMANDS = {
    'governance-tests': 'python -B -m unittest discover -s tests/governance',
    'documentation-checks': 'python -B scripts/governance/check_docs.py',
    'security-checks': 'python -B scripts/governance/security_check.py',
    'pilot-checks': 'python -B experiments/java-pilot/verify_integrity.py',
}


def last_handoff(state):
    rotation = state.rotation
    task = state.tasks.get(rotation.get('last_confirmed_task_id'))
    require(task and state.record(task), 'Missing canonical previous acceptance')
    record = state.record(task)
    key = f"{task['plan_id']}:{record['head_sha']}"
    require(rotation['last_accepted_handoff_key'] == key, 'Rotation and acceptance key disagree')
    pr = state.verified_acceptance(task)
    require(pr['merge_commit_sha'] == rotation['last_confirmed_commit'],
            'Rotation and accepted merge revision disagree')
    event = state.events.get('TASK_ACCEPTED:task:' + key)
    if 'developer' in record:
        advanced = state.events.get('ROTATION_ADVANCED:task:' + key)
        require(event and event['pr'] == record['pr'] and event.get('head_sha') == record['head_sha']
                and event['commit_sha'] == pr['merge_commit_sha'] and advanced
                and advanced['commit_sha'] == pr['merge_commit_sha']
                and advanced['next_index'] == rotation['rotation_index']
                and advanced['next_task'] == rotation['active_task_plan_id']
                and advanced['next_owner'] == rotation['active_owner'],
                'Acceptance, append-only history and rotation disagree')
    return task, record, (event or {}).get('contributors', {}).get('actual_implementer')


def post_migration_handoff(state, phases):
    intent = json.loads(state.repo.blob(state.main, HANDOFF_INTENT))
    owner, selected = intent['intended_developer'], intent['reconciled_task_id']
    evidence = intent['reconciliation_evidence']
    require(intent['schema_version'] == 1 and intent['intent'] == 'FROZEN_RELATED_WORK'
            and owner == 'Yaman-A-E' and ((selected is None and evidence is None)
                                        or (selected in state.tasks and https(evidence))),
            'Invalid protected post-migration handoff record')
    active = state.tasks[state.rotation['active_task_plan_id']]
    assignment = f"{active['plan_id']} / #{active['issue_number']} ({state.rotation['active_owner']})"
    missing = [phase for phase in MIGRATIONS if not phases.get(phase, {}).get('acceptance')]
    if missing:
        return f'Alperen frozen-related handoff awaits trusted migration acceptance: {", ".join(missing)}.'
    if selected is None:
        return (f'Alperen frozen-related handoff requires an exact protected task decision. '
                f'Reconcile the current assignment {assignment} before generating a prompt.')
    task = state.tasks[selected]
    record = state.record(task)
    if record:
        require(record.get('developer') == owner, 'Frozen-related task acceptance has a different developer')
        pr = state.verified_acceptance(task)
        activation = phases[MIGRATIONS[-1]]['acceptance']['commit_sha']
        ancestry = state.api.call(f"/compare/{activation}...{pr['merge_commit_sha']}")
        require(ancestry['status'] == 'ahead' and ancestry['merge_base_commit']['sha'] == activation,
                'Frozen-related acceptance must follow migration integration')
        return None
    if active['plan_id'] != selected or state.rotation['active_owner'] != owner:
        return f'Reconcile {assignment} with the protected decision for {selected} ({owner}).'
    return None


def product_status(state):
    rotation = state.rotation
    active = state.tasks[rotation['active_task_plan_id']]
    phases = phase_records(state.events)
    incomplete = {task_id: [dep for dep in task['dependencies'] if not state.record(state.tasks[dep])]
                  for task_id, task in state.tasks.items() if not state.record(task)}
    blockers = []
    last = None
    try:
        task, record, implementer = last_handoff(state)
        last = dict(task=task['plan_id'], pr=record['pr'], actual_implementer=implementer,
                    head=record['head_sha'], merge=rotation['last_confirmed_commit'])
    except (Rejected, RuntimeError) as exc:
        blockers.append(str(exc))
    if state.api.call(f"/issues/{active['issue_number']}")['state'] != 'open':
        blockers.append('Active issue is not open. Reconcile canonical acceptance first.')
    if active['plan_id'] not in incomplete or incomplete[active['plan_id']]:
        blockers.append('Active task acceptance or dependencies conflict with the trusted assignment.')
    if phases.get(active['phase'], {}).get('status') == 'LOCKED':
        blockers.append('Active task belongs to a locked phase.')
    if state.repo.text('ls-tree', state.main, HANDOFF_INTENT):
        try:
            blocker = post_migration_handoff(state, phases)
            if blocker:
                blockers.append(blocker)
        except (Rejected, RuntimeError) as exc:
            blockers.append(str(exc))
    try:
        verify_checks(state.api, state.main, {'pilot-checks'})
    except (Rejected, RuntimeError) as exc:
        blockers.append(str(exc) + f'. Pilot repair evidence: https://github.com/{REPO}/pull/48')
    state.recheck()
    return dict(repository=REPO, source_main_sha=state.main, active_task=active['plan_id'],
                active_owner=rotation['active_owner'], last_accepted=last, incomplete=incomplete,
                locked_product_phases=sorted(p for p in phases if p not in MIGRATIONS
                                             and phases[p].get('status') == 'LOCKED'),
                migration={p: phases.get(p, {}).get('status') or
                           ('ACCEPTED' if phases.get(p, {}).get('acceptance') else 'UNRECORDED')
                           for p in MIGRATIONS},
                conditional_next_owner=rotation['next_owner_if_accepted'], blockers=blockers)


def render_prompt(state):
    status = product_status(state)
    require(not status['blockers'], ' '.join(status['blockers']))
    require(state.repo.text('ls-tree', state.main, HANDOFF_INTENT),
            'Protected post-migration handoff record is missing')
    active_protection(state.api)
    task = state.tasks[status['active_task']]
    require(task['plan_id'] != 'F01-GOV', 'Protected governance work requires a separate contract')
    gate.check_dependencies(task, state.tasks, state.accepted, state.api, state.plan)
    prefix = re.compile(rf"(feature|fix|docs|test|chore)/{task['issue_number']}-[a-z0-9][a-z0-9-]*")
    for pr in state.api.pages('/pulls?state=closed&base=main'):
        if prefix.fullmatch(pr['head']['ref']):
            candidate = state.api.call(f"/pulls/{pr['number']}")
            require(not candidate.get('merged'), 'Active task is merged pending canonical acceptance')
    previous = status['last_accepted']
    evidence = state.record(state.tasks[previous['task']])['evidence']
    sources = ('AGENTS.md', PLAN, ACCEPTANCE, POLICY, HANDOFF_INTENT, *PRODUCT_DOCS, *SKILLS)
    if state.raw_history:
        sources += (HISTORY,)
    revisions = {}
    for source in sources:
        require(state.repo.blob(state.main, source).strip(), 'Empty source: ' + source)
        revisions[source] = state.repo.text('rev-parse', f'{state.main}:{source}')
    checks = {name: COMMANDS.get(name, 'Use the reviewed task-specific command from the applicable workflow. '
                                  'If the task adds this workflow, review its actual command before execution.')
              for name in sorted(gate.required_checks(
                  task, [{'filename': path} for path in task['allowed_paths']]))}
    scope = '\n'.join('- `' + path + '`' for path in task['allowed_paths'])
    dependencies = '\n'.join(f"- {dep} via PR #{state.record(state.tasks[dep])['pr']}"
                             for dep in task['dependencies']) or 'None registered.'
    criteria = '\n'.join('- ' + line for line in task['acceptance'])
    intent = json.loads(state.repo.blob(state.main, HANDOFF_INTENT))
    if task['plan_id'] == intent['reconciled_task_id']:
        scope += '\n\nProtected handoff decision: ' + intent['reconciliation_evidence']
    root = f'https://github.com/{REPO}'
    links = lambda paths: '\n'.join(f'- [{path}]({root}/blob/{state.main}/{path})' for path in paths)
    sections = {
        'Project identity': 'Project Genesis v3.0 · preparation only',
        'Repository': REPO,
        'Verified main SHA': f'`{state.main}`',
        'Previous accepted task': f"{previous['task']} via PR #{previous['pr']}",
        'Previous implementer': previous['actual_implementer'] or 'Unknown in verified contribution evidence.',
        'Previous acceptance evidence': '\n'.join(f'- {url}' for url in evidence),
        'Current authorized developer': status['active_owner'],
        'Next task ID': task['plan_id'],
        'Related issue': f"[#{task['issue_number']}]({root}/issues/{task['issue_number']})",
        'Objective': task['objective'],
        'Dependencies': dependencies,
        'Relevant SRS': links(PRODUCT_DOCS[:2]),
        'Relevant architecture': links(PRODUCT_DOCS[2:]),
        'In scope': task['deliverable'],
        'Out of scope': 'Unrelated product work, governance or rotation changes, and all paths outside reviewed scope.',
        'Allowed paths': scope,
        'Protected paths': '\n'.join('- `' + path + '`' for path in FROZEN)
                           + '\n\nApply the pinned governance policy to all other protected paths.',
        'Implementation requirements': task['title'] + '. Use the task-execution skill to bind the work '
                                       'to a numbered branch and a fresh explicit authorization from the named developer.',
        'Acceptance criteria': criteria,
        'Verification commands': '\n'.join(f'- {name} · {command}' for name, command in checks.items()),
        'History requirements': 'Keep contributor roles and verified revision evidence separate in the handoff.',
        'Failure conditions': 'Stop for stale provenance, changed assignment or scope, missing acceptance, '
                              'a blocker, or a missing or failed required check.',
        'Human review procedure': 'Review the exact diff, pinned source and actual verification results.',
        'PUSHLA publication procedure': links(SKILLS[2:]) + '\n\nAwait explicit PUSHLA for the reviewed diff.',
        'Final stop condition': 'Prompt preparation ends here. The named developer authorizes task execution separately.',
        'Source provenance': '\n'.join(f'- `{path}` · `{revision}`' for path, revision in revisions.items())
                             + '\n\nRevalidate this exact prompt against live main before use.',
    }
    require(state.api.call(f"/issues/{task['issue_number']}")['state'] == 'open',
            'Task changed during prompt preparation')
    state.recheck()
    return '# NEXT_STEP_PROMPT\n' + ''.join(f'\n## {key}\n\n{value}\n' for key, value in sections.items())


def validate_prompt(state, raw):
    require(raw == render_prompt(state).encode('utf-8'), 'Invalid or stale prompt provenance')


def archive_prompt(state, prompt):
    task = state.rotation['active_task_plan_id']
    require(re.fullmatch(r'[A-Z0-9-]+', task), 'Unsafe task ID for archival')
    path = f'docs/handoffs/{task}/NEXT_STEP_PROMPT.md'
    require(state.repo.file_state(path) is None, 'Prompt already exists; review it before replacing')
    destination = state.repo.root / path
    state.recheck()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open('xb') as stream:
        stream.write(prompt.encode('utf-8'))
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['status', 'draft', 'validate'])
    parser.add_argument('--prompt', type=Path)
    parser.add_argument('--archive', action='store_true')
    args = parser.parse_args()
    try:
        require(args.prompt is None or args.command == 'validate', 'Use --prompt only for validation')
        require(not args.archive or args.command == 'draft', 'Use --archive only when drafting')
        state = State(Repository(), GitHub(REPO, follow_redirects=False),
                      activated=args.command != 'status')
        if args.command == 'status':
            print(json.dumps(product_status(state), ensure_ascii=True, indent=2))
            return
        if args.command == 'validate':
            require(args.prompt, 'Supply --prompt for provenance validation')
            validate_prompt(state, args.prompt.read_bytes())
            print('PROMPT_PROVENANCE_VERIFIED')
            return
        prompt = render_prompt(state)
        if args.archive:
            print(archive_prompt(state, prompt))
        else:
            sys.stdout.buffer.write(prompt.encode('utf-8'))
    except (Rejected, RuntimeError, OSError, KeyError, ValueError, TypeError,
            subprocess.TimeoutExpired) as exc:
        parser.exit(1, f'NEXT_STEP_BLOCKED: {exc}\n')


if __name__ == '__main__':
    main()
