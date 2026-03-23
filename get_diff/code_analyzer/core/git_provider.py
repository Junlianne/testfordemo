import requests
import os
from abc import ABC, abstractmethod
from .utils import retry

class GitProvider(ABC):
    @abstractmethod
    def get_pr_details(self, pr_info):
        pass

    @abstractmethod
    def get_diff(self, pr_info):
        pass

class GitHubProvider(GitProvider):
    def __init__(self, token=None):
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"

    @retry(exceptions=(requests.RequestException, Exception), tries=3, delay=1, backoff=2)
    def get_pr_details(self, pr_info):
        owner = pr_info["owner"]
        repo = pr_info["repo"]
        pr_id = pr_info["pr_id"]
        
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_id}"
        response = requests.get(url, headers=self.headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "title": data.get("title"),
                "description": data.get("body"),
                "author": data.get("user", {}).get("login"),
                "state": data.get("state"),
                "url": data.get("html_url")
            }
        else:
            raise Exception(f"GitHub API Error: {response.status_code} - {response.text}")

    @retry(exceptions=(requests.RequestException, Exception), tries=3, delay=1, backoff=2)
    def get_diff(self, pr_info):
        owner = pr_info["owner"]
        repo = pr_info["repo"]
        pr_id = pr_info["pr_id"]
        
        # Requesting the diff media type
        headers = self.headers.copy()
        headers["Accept"] = "application/vnd.github.v3.diff"
        
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_id}"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return response.text
        else:
            raise Exception(f"GitHub API Error fetching diff: {response.status_code} - {response.text}")

class GitLabProvider(GitProvider):
    def __init__(self, token=None, base_url="https://gitlab.com/api/v4"):
        self.token = token
        self.base_url = base_url
        self.headers = {}
        if self.token:
            self.headers["Private-Token"] = self.token

    @retry(exceptions=(requests.RequestException, Exception), tries=3, delay=1, backoff=2)
    def get_pr_details(self, pr_info):
        # GitLab uses URL-encoded path as ID
        project_path = pr_info["repo_path"].replace("/", "%2F")
        mr_id = pr_info["pr_id"]
        
        # Override base_url if provided in parsed info
        base_url = pr_info.get("base_url", self.base_url)
        
        url = f"{base_url}/projects/{project_path}/merge_requests/{mr_id}"
        response = requests.get(url, headers=self.headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "title": data.get("title"),
                "description": data.get("description"),
                "author": data.get("author", {}).get("username"),
                "state": data.get("state"),
                "url": data.get("web_url")
            }
        else:
            raise Exception(f"GitLab API Error: {response.status_code} - {response.text}")

    @retry(exceptions=(requests.RequestException, Exception), tries=3, delay=1, backoff=2)
    def get_diff(self, pr_info):
        project_path = pr_info["repo_path"].replace("/", "%2F")
        mr_id = pr_info["pr_id"]
        
        # Override base_url if provided in parsed info
        base_url = pr_info.get("base_url", self.base_url)
        
        url = f"{base_url}/projects/{project_path}/merge_requests/{mr_id}/changes"
        response = requests.get(url, headers=self.headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            changes = data.get("changes", [])
            diff_text = ""
            for change in changes:
                diff_text += f"--- {change.get('old_path')}\n+++ {change.get('new_path')}\n"
                diff_text += change.get("diff", "") + "\n"
            return diff_text
        else:
            raise Exception(f"GitLab API Error fetching diff: {response.status_code} - {response.text}")

class GiteeProvider(GitProvider):
    def __init__(self, token=None):
        self.token = token
        self.base_url = "https://gitee.com/api/v5"

    @retry(exceptions=(requests.RequestException, Exception), tries=3, delay=1, backoff=2)
    def get_pr_details(self, pr_info):
        owner = pr_info["owner"]
        repo = pr_info["repo"]
        pr_id = pr_info["pr_id"]
        
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_id}"
        params = {}
        if self.token:
            params["access_token"] = self.token
            
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "title": data.get("title"),
                "description": data.get("body"),
                "author": data.get("user", {}).get("login"),
                "state": data.get("state"),
                "url": data.get("html_url")
            }
        else:
            raise Exception(f"Gitee API Error: {response.status_code} - {response.text}")

    @retry(exceptions=(requests.RequestException, Exception), tries=3, delay=1, backoff=2)
    def get_diff(self, pr_info):
        owner = pr_info["owner"]
        repo = pr_info["repo"]
        pr_id = pr_info["pr_id"]
        
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_id}/files"
        params = {}
        if self.token:
            params["access_token"] = self.token
            
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            files = response.json()
            diff_text = ""
            for file in files:
                diff_text += f"--- {file.get('filename')}\n+++ {file.get('filename')}\n"
                diff_text += file.get("patch", "") + "\n"
            return diff_text
        else:
            raise Exception(f"Gitee API Error fetching diff: {response.status_code} - {response.text}")

class BitbucketProvider(GitProvider):
    def __init__(self, token=None):
        self.token = token
        self.base_url = "https://api.bitbucket.org/2.0"
        self.headers = {"Accept": "application/json"}
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"

    @retry(exceptions=(requests.RequestException, Exception), tries=3, delay=1, backoff=2)
    def get_pr_details(self, pr_info):
        owner = pr_info["owner"]
        repo = pr_info["repo"]
        pr_id = pr_info["pr_id"]
        
        url = f"{self.base_url}/repositories/{owner}/{repo}/pullrequests/{pr_id}"
        response = requests.get(url, headers=self.headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "title": data.get("title"),
                "description": data.get("description"),
                "author": data.get("author", {}).get("display_name"),
                "state": data.get("state"),
                "url": data.get("links", {}).get("html", {}).get("href")
            }
        else:
            raise Exception(f"Bitbucket API Error: {response.status_code} - {response.text}")

    @retry(exceptions=(requests.RequestException, Exception), tries=3, delay=1, backoff=2)
    def get_diff(self, pr_info):
        owner = pr_info["owner"]
        repo = pr_info["repo"]
        pr_id = pr_info["pr_id"]
        
        url = f"{self.base_url}/repositories/{owner}/{repo}/pullrequests/{pr_id}/diff"
        response = requests.get(url, headers=self.headers, timeout=10)
        
        if response.status_code == 200:
            return response.text
        else:
            raise Exception(f"Bitbucket API Error fetching diff: {response.status_code} - {response.text}")
