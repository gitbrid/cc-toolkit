import json
import urllib.error
import unittest
from email.message import Message
from unittest import mock

from github_api import GitHubRateLimitError, search_new_repos, get_repo, get_readme_text, _request


class TestGitHubApi(unittest.TestCase):
    def test_search_new_repos_parses_items(self):
        payload = {"items": [{"full_name": "a/b", "stargazers_count": 10}]}
        with mock.patch("urllib.request.urlopen") as m:
            m.return_value.__enter__.return_value.read.return_value = json.dumps(payload).encode()
            result = search_new_repos("2026-01-01", "2026-01-04", token="x")
        self.assertEqual(result[0]["full_name"], "a/b")

    def test_get_repo(self):
        with mock.patch("urllib.request.urlopen") as m:
            m.return_value.__enter__.return_value.read.return_value = json.dumps({"full_name": "a/b"}).encode()
            result = get_repo("a", "b")
        self.assertEqual(result["full_name"], "a/b")

    def test_get_readme_text_decodes_base64(self):
        import base64

        payload = {"content": base64.b64encode(b"# Hello\nworld").decode()}
        with mock.patch("urllib.request.urlopen") as m:
            m.return_value.__enter__.return_value.read.return_value = json.dumps(payload).encode()
            result = get_readme_text("a", "b")
        self.assertIn("world", result)

    def test_request_fails_fast_on_rate_limit(self):
        headers = Message()
        headers["X-RateLimit-Remaining"] = "0"
        err = urllib.error.HTTPError("https://api.github.com/x", 403, "Forbidden", headers, None)
        with mock.patch("urllib.request.urlopen", side_effect=err):
            with self.assertRaises(GitHubRateLimitError):
                _request("https://api.github.com/x")


if __name__ == "__main__":
    unittest.main()
