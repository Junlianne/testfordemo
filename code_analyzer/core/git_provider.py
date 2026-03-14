import requests
import os
from abc import ABC, abstractmethod

class GitProvider(ABC):
    @abstractmethod
    def get_pr_details(self, pr_info):
        pass

    @abstractmethod
    def get_diff(self, pr_info):
        pass

    @abstractmethod
    def get_open_prs(self, repo_info):
        pass

class GitHubProvider(GitProvider):
    def __init__(self, token=None):
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"

    def get_pr_details(self, pr_info):
        owner = pr_info["owner"]
        repo = pr_info["repo"]
        pr_id = pr_info["pr_id"]
        
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_id}"
        response = requests.get(url, headers=self.headers)
        
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

    def get_diff(self, pr_info):
        owner = pr_info["owner"]
        repo = pr_info["repo"]
        pr_id = pr_info["pr_id"]
        
        # Requesting the diff media type
        headers = self.headers.copy()
        headers["Accept"] = "application/vnd.github.v3.diff"
        
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_id}"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.text
        else:
            raise Exception(f"GitHub API Error fetching diff: {response.status_code} - {response.text}")

    def get_open_prs(self, repo_info):
        owner = repo_info["owner"]
        repo = repo_info["repo"]
        
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls?state=open"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            data = response.json()
            return [{
                "id": pr.get("number"),
                "title": pr.get("title"),
                "url": pr.get("html_url"),
                "updated_at": pr.get("updated_at"),
                "author": pr.get("user", {}).get("login")
            } for pr in data]
        else:
            raise Exception(f"GitHub API Error fetching PRs: {response.status_code} - {response.text}")

class GitLabProvider(GitProvider):
    def __init__(self, token=None, base_url="https://gitlab.com/api/v4"):
        self.token = token
        self.base_url = base_url
        self.headers = {}
        if self.token:
            self.headers["Private-Token"] = self.token

    def get_pr_details(self, pr_info):
        # GitLab uses URL-encoded path as ID
        project_path = pr_info["repo_path"].replace("/", "%2F")
        mr_id = pr_info["pr_id"]
        
        url = f"{self.base_url}/projects/{project_path}/merge_requests/{mr_id}"
        response = requests.get(url, headers=self.headers)
        
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

    def get_diff(self, pr_info):
        project_path = pr_info["repo_path"].replace("/", "%2F")
        mr_id = pr_info["pr_id"]
        
        # GitLab MR changes API gives structured diffs, but we want a raw diff for simplicity if possible.
        # Or we can construct a text diff from the changes API.
        # The .diff endpoint on the MR web URL is often available, but via API we use /changes
        
        url = f"{self.base_url}/projects/{project_path}/merge_requests/{mr_id}/changes"
        response = requests.get(url, headers=self.headers)
        
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

    def get_open_prs(self, repo_info):
        project_path = repo_info["repo_path"].replace("/", "%2F")
        
        url = f"{self.base_url}/projects/{project_path}/merge_requests?state=opened"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            data = response.json()
            return [{
                "id": mr.get("iid"),
                "title": mr.get("title"),
                "url": mr.get("web_url"),
                "updated_at": mr.get("updated_at"),
                "author": mr.get("author", {}).get("username")
            } for mr in data]
        else:
            raise Exception(f"GitLab API Error fetching MRs: {response.status_code} - {response.text}")
