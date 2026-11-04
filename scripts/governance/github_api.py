"""Small stdlib GitHub client. No credential storage or shell interpolation."""
import json
import os
import re
import urllib.error
import urllib.request
from urllib.parse import unquote

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class GitHub:
    def __init__(self, repo=None, *, follow_redirects=True):
        self.repo = repo or os.environ['GITHUB_REPOSITORY']
        self.root = 'https://api.github.com/repos/' + self.repo
        self.open = (urllib.request.urlopen if follow_redirects
                     else urllib.request.build_opener(NoRedirect()).open)

    def call(self, path, method='GET', data=None, missing_ok=False):
        decoded = unquote(path.split('?', 1)[0])
        compare = re.fullmatch(r'/compare/[0-9a-f]{40}\.\.\.[0-9a-f]{40}', path)
        if not compare and (not path.startswith('/') or decoded.startswith('//')
                            or decoded == '/compare' or decoded.startswith('/compare/')
                            or '..' in path or '..' in decoded or '\\' in decoded):
            raise ValueError('Invalid repository API path')
        return self._request(self.root if path == '/' else self.root + path, method, data, missing_ok)

    def identity(self):
        return self._request('https://api.github.com/user')

    def review_decision(self, number):
        owner, name = self.repo.split('/')
        query = ('query($owner:String!,$name:String!,$number:Int!){repository(owner:$owner,name:$name)'
                 '{pullRequest(number:$number){reviewDecision}}}')
        result = self._request('https://api.github.com/graphql', 'POST', {
            'query': query, 'variables': dict(owner=owner, name=name, number=number),
        })
        if result.get('errors'):
            raise RuntimeError('GitHub could not verify the pull request review decision')
        return result['data']['repository']['pullRequest']['reviewDecision']

    def _request(self, url, method='GET', data=None, missing_ok=False):
        req = urllib.request.Request(url, method=method,
            data=None if data is None else json.dumps(data).encode(), headers={
                'Authorization': 'Bearer ' + os.environ['GH_TOKEN'],
                'Accept': 'application/vnd.github+json',
                'X-GitHub-Api-Version': '2022-11-28',
                'Content-Type': 'application/json'})
        try:
            with self.open(req, timeout=30) as response:
                raw = response.read()
                return json.loads(raw) if raw else None
        except urllib.error.HTTPError as exc:
            if exc.code == 404 and missing_ok:
                return None
            raise RuntimeError(f'GitHub API {method} {url}: HTTP {exc.code}') from None

    def pages(self, path, key=None):
        rows = []
        for page in range(1, 101):
            sep = '&' if '?' in path else '?'
            result = self.call(f'{path}{sep}per_page=100&page={page}')
            batch = result[key] if key else result
            rows.extend(batch)
            if len(batch) < 100:
                return rows
        raise RuntimeError('Pagination exceeded safe limit')
