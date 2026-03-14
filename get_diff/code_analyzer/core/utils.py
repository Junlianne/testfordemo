import re
from urllib.parse import urlparse

def parse_git_url(url):
    """
    Parses a GitHub or GitLab URL and returns provider, owner, repo, and pull_request_id.
    
    Supported formats:
    GitHub: https://github.com/owner/repo/pull/123
    GitLab: https://gitlab.com/owner/repo/-/merge_requests/123
    """
    parsed = urlparse(url)
    path_parts = parsed.path.strip("/").split("/")
    
    if "github.com" in parsed.netloc:
        if len(path_parts) >= 4 and path_parts[2] == "pull":
            return {
                "provider": "github",
                "owner": path_parts[0],
                "repo": path_parts[1],
                "pr_id": path_parts[3]
            }
            
    elif "gitlab.com" in parsed.netloc:
        # GitLab URLs can be complex with subgroups, but standard is owner/repo/-/merge_requests/id
        # We will look for 'merge_requests' and work backwards
        try:
            mr_index = path_parts.index("merge_requests")
            pr_id = path_parts[mr_index + 1]
            
            # Repo path is everything before - or before merge_requests if - is missing
            if "-" in path_parts:
                dash_index = path_parts.index("-")
                repo_path = "/".join(path_parts[:dash_index])
            else:
                repo_path = "/".join(path_parts[:mr_index])
                
            return {
                "provider": "gitlab",
                "repo_path": repo_path, # GitLab uses full path as ID often
                "pr_id": pr_id
            }
        except (ValueError, IndexError):
            pass
            
    return None
