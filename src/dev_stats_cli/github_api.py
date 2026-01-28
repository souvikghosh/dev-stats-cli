"""GitHub API client for fetching user and repository statistics."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import requests

BASE_URL = "https://api.github.com"
TIMEOUT = 10


class GitHubError(Exception):
    """Exception raised for GitHub API errors."""

    pass


@dataclass
class UserStats:
    """GitHub user statistics."""

    username: str
    name: str | None
    bio: str | None
    public_repos: int
    followers: int
    following: int
    created_at: datetime
    avatar_url: str | None


@dataclass
class RepoStats:
    """Repository statistics."""

    name: str
    full_name: str
    description: str | None
    language: str | None
    stars: int
    forks: int
    watchers: int
    open_issues: int
    created_at: datetime
    updated_at: datetime
    is_fork: bool
    size_kb: int


@dataclass
class ContributionStats:
    """User contribution statistics."""

    total_commits: int
    total_prs: int
    total_issues: int
    total_reviews: int
    repos_contributed_to: int


def _make_request(
    endpoint: str,
    token: str | None = None,
    params: dict | None = None,
) -> Any:
    """Make a request to the GitHub API."""
    url = f"{BASE_URL}/{endpoint}"
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        response = requests.get(url, headers=headers, params=params, timeout=TIMEOUT)
        if response.status_code == 404:
            raise GitHubError("Resource not found")
        if response.status_code == 403:
            raise GitHubError("Rate limit exceeded or access denied")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise GitHubError(f"API request failed: {e}") from e


def get_user(username: str, token: str | None = None) -> UserStats:
    """Get user profile information."""
    data = _make_request(f"users/{username}", token)
    return UserStats(
        username=data["login"],
        name=data.get("name"),
        bio=data.get("bio"),
        public_repos=data["public_repos"],
        followers=data["followers"],
        following=data["following"],
        created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),
        avatar_url=data.get("avatar_url"),
    )


def get_user_repos(
    username: str,
    token: str | None = None,
    include_forks: bool = False,
) -> list[RepoStats]:
    """Get user's repositories."""
    repos = []
    page = 1
    per_page = 100

    while True:
        data = _make_request(
            f"users/{username}/repos",
            token,
            params={"page": page, "per_page": per_page, "sort": "updated"},
        )

        if not data:
            break

        for repo in data:
            if not include_forks and repo["fork"]:
                continue

            repos.append(
                RepoStats(
                    name=repo["name"],
                    full_name=repo["full_name"],
                    description=repo.get("description"),
                    language=repo.get("language"),
                    stars=repo["stargazers_count"],
                    forks=repo["forks_count"],
                    watchers=repo["watchers_count"],
                    open_issues=repo["open_issues_count"],
                    created_at=datetime.fromisoformat(
                        repo["created_at"].replace("Z", "+00:00")
                    ),
                    updated_at=datetime.fromisoformat(
                        repo["updated_at"].replace("Z", "+00:00")
                    ),
                    is_fork=repo["fork"],
                    size_kb=repo["size"],
                )
            )

        if len(data) < per_page:
            break
        page += 1

    return repos


def get_repo_languages(owner: str, repo: str, token: str | None = None) -> dict[str, int]:
    """Get language breakdown for a repository."""
    return _make_request(f"repos/{owner}/{repo}/languages", token)


def calculate_language_stats(repos: list[RepoStats]) -> dict[str, int]:
    """Calculate language usage across repositories."""
    languages: dict[str, int] = {}
    for repo in repos:
        if repo.language:
            languages[repo.language] = languages.get(repo.language, 0) + 1
    return dict(sorted(languages.items(), key=lambda x: x[1], reverse=True))


def calculate_summary_stats(repos: list[RepoStats]) -> dict[str, Any]:
    """Calculate summary statistics from repositories."""
    total_stars = sum(r.stars for r in repos)
    total_forks = sum(r.forks for r in repos)
    total_size = sum(r.size_kb for r in repos)

    languages = calculate_language_stats(repos)
    top_language = list(languages.keys())[0] if languages else None

    return {
        "total_repos": len(repos),
        "total_stars": total_stars,
        "total_forks": total_forks,
        "total_size_mb": round(total_size / 1024, 2),
        "average_stars": round(total_stars / len(repos), 1) if repos else 0,
        "top_language": top_language,
        "languages": languages,
    }
