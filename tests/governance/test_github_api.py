import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts/governance'))
from github_api import GitHub
from repository_identity import DESTINATION


class GitHubComparePathTests(unittest.TestCase):
    def test_exact_lowercase_sha_pair_and_ordinary_endpoint_reach_http_client(self):
        comparison = f"/compare/{'a' * 40}...{'b' * 40}"
        for path in (comparison, '/pulls/49/files?per_page=100'):
            with self.subTest(path=path), patch.dict('os.environ', {'GH_TOKEN': 'fixture'}), patch(
                    'github_api.urllib.request.urlopen') as open_url:
                client = GitHub(DESTINATION)
                open_url.return_value.__enter__.return_value.read.return_value = b'{"verified":true}'
                self.assertEqual({'verified': True}, client.call(path))
                self.assertEqual(client.root + path, open_url.call_args.args[0].full_url)

    def test_malformed_comparisons_and_traversal_never_reach_http_client(self):
        head, base = 'a' * 40, 'b' * 40
        for path in (f'/compare/{base}..{head}', f'/compare/{base}....{head}',
                     f'/compare/{base.upper()}...{head}', f'/compare/{base[:-1]}...{head}',
                     f'/compare/{base}...{head}?page=1', f'/compare/{base}...{head}/files',
                     '/compare/main', '/compare%2Fmain', '/issues/../pulls',
                     '/issues/%2e%2e/pulls', '/issues/%5c../pulls', '//example.org',
                     'https://example.org/compare/a...b'):
            with self.subTest(path=path), patch('github_api.urllib.request.urlopen') as open_url:
                with self.assertRaisesRegex(ValueError, 'Invalid repository API path'):
                    GitHub(DESTINATION).call(path)
                open_url.assert_not_called()
