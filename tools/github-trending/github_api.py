import base64
import json
import time
import urllib.error
import urllib.request


class GitHubRateLimitError(Exception):
    pass


def _request(url, token=None, retries=3):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "codex-toolbox",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (403, 429):
                time.sleep(8 * (attempt + 1))
                continue
            raise
        except (urllib.error.URLError, TimeoutError):
            time.sleep(5 * (attempt + 1))
    raise GitHubRateLimitError(f"request failed after retries: {url}")


def search_new_repos(start, end, top=10, token=None):
    url = (
        "https://api.github.com/search/repositories?q="
        f"created:{start}..{end}&sort=stars&order=desc&per_page={top}"
    )
    data = _request(url, token)
    return data.get("items", [])


def get_repo(owner, repo, token=None):
    return _request(f"https://api.github.com/repos/{owner}/{repo}", token)


def get_readme_text(owner, repo, token=None):
    data = _request(f"https://api.github.com/repos/{owner}/{repo}/readme", token)
    return base64.b64decode(data.get("content", "")).decode("utf-8", errors="replace")
