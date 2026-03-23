import unittest
from core.utils import parse_git_url, InvalidPRUrlError, UnsupportedProviderError

class TestUtils(unittest.TestCase):
    def test_parse_github_url(self):
        url = "https://github.com/owner/repo/pull/123"
        result = parse_git_url(url)
        self.assertEqual(result["provider"], "github")
        self.assertEqual(result["owner"], "owner")
        self.assertEqual(result["repo"], "repo")
        self.assertEqual(result["pr_id"], "123")

    def test_parse_gitlab_url(self):
        url = "https://gitlab.com/owner/repo/-/merge_requests/123"
        result = parse_git_url(url)
        self.assertEqual(result["provider"], "gitlab")
        self.assertEqual(result["repo_path"], "owner/repo")
        self.assertEqual(result["pr_id"], "123")
        self.assertEqual(result["base_url"], "https://gitlab.com/api/v4")

    def test_parse_gitee_url(self):
        url = "https://gitee.com/owner/repo/pulls/123"
        result = parse_git_url(url)
        self.assertEqual(result["provider"], "gitee")
        self.assertEqual(result["owner"], "owner")
        self.assertEqual(result["repo"], "repo")
        self.assertEqual(result["pr_id"], "123")

    def test_parse_bitbucket_url(self):
        url = "https://bitbucket.org/owner/repo/pull-requests/123"
        result = parse_git_url(url)
        self.assertEqual(result["provider"], "bitbucket")
        self.assertEqual(result["owner"], "owner")
        self.assertEqual(result["repo"], "repo")
        self.assertEqual(result["pr_id"], "123")

    def test_invalid_url(self):
        with self.assertRaises(InvalidPRUrlError):
            parse_git_url("")

    def test_unsupported_provider(self):
        with self.assertRaises(UnsupportedProviderError):
            parse_git_url("https://unknown.com/owner/repo/pull/123")

if __name__ == '__main__':
    unittest.main()
