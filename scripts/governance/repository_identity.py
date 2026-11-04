"""Proposed transfer bridge for one existing repository, never a generic repo alias."""
import copy
import os
import subprocess


ORIGINAL = 'caferkilinc/refactoring-ai-generated-code'
DESTINATION = 'refactoring-ai-code/refactoring-ai-generated-code'
REPOSITORY_ID = 1391020028
ALIASES = frozenset((ORIGINAL, DESTINATION))


def repository_urls(repository):
    if repository not in ALIASES:
        raise ValueError('Repository is outside the exact transfer scope')
    return {f'https://github.com/{repository}', f'https://github.com/{repository}.git',
            f'git@github.com:{repository}.git', f'ssh://git@github.com/{repository}.git'}


def current_repository(environment=None, origin=None):
    environment = os.environ if environment is None else environment
    declared = environment.get('GITHUB_REPOSITORY')
    if declared is not None and declared not in ALIASES:
        raise ValueError('Unexpected GitHub repository identity')
    if origin is None:
        result = subprocess.run(['git', 'remote', 'get-url', 'origin'], capture_output=True,
                                text=True, timeout=10)
        origin = result.stdout.strip() if result.returncode == 0 else ''
    selected = next((name for name in ALIASES if origin in repository_urls(name)), None)
    if declared and selected and declared != selected:
        raise ValueError('GitHub workflow repository and Git origin disagree')
    return declared or selected or ORIGINAL


def verify_destination(api):
    info = api.call('/')
    if (info.get('full_name') != DESTINATION or type(info.get('id')) is not int
            or info['id'] != REPOSITORY_ID):
        raise ValueError('Transfer destination is not the original immutable repository ID')
    return info


def effective_plan(plan, api, repository):
    """Adapt runtime identity only; never rewrite historical registry bytes or roles."""
    source = plan.get('repository')
    if repository not in ALIASES or source not in ALIASES:
        raise ValueError('Unapproved registry or runtime repository')
    if repository == ORIGINAL:
        if source != ORIGINAL:
            raise ValueError('Registry has moved; old runtime identity is stale')
        return plan
    verify_destination(api)
    result = copy.deepcopy(plan)
    result['repository'] = DESTINATION
    return result
