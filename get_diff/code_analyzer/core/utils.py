import re
from urllib.parse import urlparse
import time
from functools import wraps

class InvalidPRUrlError(ValueError):
    """Raised when the PR URL is invalid or malformed."""
    pass

class UnsupportedProviderError(ValueError):
    """Raised when the Git provider is not supported."""
    pass

def parse_git_url(url):
    """
    Parses a GitHub, GitLab, Gitee, or Bitbucket URL and returns provider, owner, repo, and pull_request_id.
    
    Supported formats:
    GitHub: https://github.com/owner/repo/pull/123
    GitLab: https://gitlab.com/owner/repo/-/merge_requests/123
    Custom GitLab: https://git.mycompany.com/owner/repo/-/merge_requests/123
    Gitee: https://gitee.com/owner/repo/pulls/123
    Bitbucket: https://bitbucket.org/owner/repo/pull-requests/123
    """
    if not url or not isinstance(url, str):
        raise InvalidPRUrlError("URL must be a non-empty string")
        
    parsed = urlparse(url.strip())
    path_parts = [p for p in parsed.path.split("/") if p]
    
    if not path_parts:
        raise InvalidPRUrlError("URL path is empty")
        
    domain = parsed.netloc.lower()

    # Check for GitHub
    if "github.com" in domain:
        if len(path_parts) >= 4 and path_parts[2] in ("pull", "pulls"):
            return {
                "provider": "github",
                "owner": path_parts[0],
                "repo": path_parts[1],
                "pr_id": path_parts[3]
            }
            
    # Check for Gitee
    elif "gitee.com" in domain:
        if len(path_parts) >= 4 and path_parts[2] in ("pulls", "pull"):
            return {
                "provider": "gitee",
                "owner": path_parts[0],
                "repo": path_parts[1],
                "pr_id": path_parts[3]
            }

    # Check for Bitbucket
    elif "bitbucket.org" in domain:
        if len(path_parts) >= 4 and path_parts[2] == "pull-requests":
            return {
                "provider": "bitbucket",
                "owner": path_parts[0],
                "repo": path_parts[1],
                "pr_id": path_parts[3]
            }
            
    # Check for GitLab (either gitlab.com or contains 'merge_requests' which implies GitLab pattern)
    elif "gitlab" in domain or "merge_requests" in path_parts:
        try:
            mr_index = path_parts.index("merge_requests")
            if mr_index + 1 < len(path_parts):
                pr_id = path_parts[mr_index + 1]
                
                # Repo path is everything before - or before merge_requests if - is missing
                if "-" in path_parts:
                    dash_index = path_parts.index("-")
                    repo_path = "/".join(path_parts[:dash_index])
                else:
                    repo_path = "/".join(path_parts[:mr_index])
                    
                return {
                    "provider": "gitlab",
                    "repo_path": repo_path,
                    "pr_id": pr_id,
                    "base_url": f"{parsed.scheme}://{domain}/api/v4"
                }
        except (ValueError, IndexError):
            pass
            
    raise UnsupportedProviderError(f"Unsupported or malformed PR URL: {url}")


def retry(exceptions=(Exception,), tries=3, delay=1, backoff=2):
    """
    Retry calling the decorated function using an exponential backoff.

    :param exceptions: tuple of exceptions to check.
    :param tries: number of times to try (not retry) before giving up.
    :param delay: initial delay between retries in seconds.
    :param backoff: backoff multiplier e.g. value of 2 will double the delay each retry.
    """
    def deco_retry(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except exceptions as e:
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)
        return f_retry
    return deco_retry
