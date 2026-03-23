import unittest
from unittest.mock import patch, MagicMock
from core.git_provider import GitHubProvider, GitLabProvider, BitbucketProvider

class TestGitProviders(unittest.TestCase):
    @patch('core.git_provider.requests.get')
    def test_github_get_pr_details_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "title": "Test PR",
            "body": "Test description",
            "user": {"login": "testuser"},
            "state": "open",
            "html_url": "https://github.com/owner/repo/pull/1"
        }
        mock_get.return_value = mock_response

        provider = GitHubProvider()
        result = provider.get_pr_details({"owner": "owner", "repo": "repo", "pr_id": "1"})
        
        self.assertEqual(result["title"], "Test PR")
        self.assertEqual(result["author"], "testuser")
        self.assertEqual(result["state"], "open")

    @patch('core.git_provider.requests.get')
    def test_bitbucket_get_pr_details_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "title": "Bitbucket PR",
            "description": "Bitbucket desc",
            "author": {"display_name": "bb_user"},
            "state": "MERGED",
            "links": {"html": {"href": "https://bitbucket.org/owner/repo/pull-requests/1"}}
        }
        mock_get.return_value = mock_response

        provider = BitbucketProvider()
        result = provider.get_pr_details({"owner": "owner", "repo": "repo", "pr_id": "1"})
        
        self.assertEqual(result["title"], "Bitbucket PR")
        self.assertEqual(result["author"], "bb_user")
        self.assertEqual(result["state"], "MERGED")

if __name__ == '__main__':
    unittest.main()
