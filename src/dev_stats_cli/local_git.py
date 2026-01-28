"""Local git repository analysis."""

from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from git import InvalidGitRepositoryError, Repo
from git.exc import GitCommandError


class LocalGitError(Exception):
    """Exception raised for local git errors."""

    pass


@dataclass
class CommitInfo:
    """Information about a commit."""

    sha: str
    message: str
    author: str
    author_email: str
    date: datetime
    files_changed: int
    insertions: int
    deletions: int


@dataclass
class LocalRepoStats:
    """Statistics for a local repository."""

    path: str
    name: str
    current_branch: str
    total_commits: int
    total_branches: int
    contributors: list[tuple[str, int]]
    first_commit: datetime | None
    last_commit: datetime | None
    total_lines_added: int
    total_lines_deleted: int


def get_repo(path: str | Path) -> Repo:
    """Get a git repository object."""
    try:
        return Repo(path)
    except InvalidGitRepositoryError as e:
        raise LocalGitError(f"Not a git repository: {path}") from e


def analyze_repo(path: str | Path) -> LocalRepoStats:
    """Analyze a local git repository."""
    repo = get_repo(path)
    path = Path(path).resolve()

    # Get branch info
    try:
        current_branch = repo.active_branch.name
    except TypeError:
        current_branch = "HEAD (detached)"

    branches = list(repo.branches)

    # Analyze commits
    commits = list(repo.iter_commits())
    total_commits = len(commits)

    # Get contributor stats
    authors: Counter[str] = Counter()
    for commit in commits:
        authors[commit.author.name] += 1

    contributors = authors.most_common()

    # Get date range
    first_commit = None
    last_commit = None
    if commits:
        last_commit = commits[0].committed_datetime
        first_commit = commits[-1].committed_datetime

    # Calculate line changes (sample recent commits for performance)
    total_added = 0
    total_deleted = 0
    sample_size = min(100, len(commits))

    for commit in commits[:sample_size]:
        try:
            stats = commit.stats.total
            total_added += stats.get("insertions", 0)
            total_deleted += stats.get("deletions", 0)
        except (GitCommandError, KeyError):
            pass

    return LocalRepoStats(
        path=str(path),
        name=path.name,
        current_branch=current_branch,
        total_commits=total_commits,
        total_branches=len(branches),
        contributors=contributors,
        first_commit=first_commit,
        last_commit=last_commit,
        total_lines_added=total_added,
        total_lines_deleted=total_deleted,
    )


def get_recent_commits(
    path: str | Path,
    count: int = 10,
    author: str | None = None,
) -> list[CommitInfo]:
    """Get recent commits from a repository."""
    repo = get_repo(path)
    commits = []

    for commit in repo.iter_commits(max_count=count):
        if author and author.lower() not in commit.author.name.lower():
            continue

        try:
            stats = commit.stats.total
        except (GitCommandError, KeyError):
            stats = {"files": 0, "insertions": 0, "deletions": 0}

        commits.append(
            CommitInfo(
                sha=commit.hexsha[:7],
                message=commit.message.strip().split("\n")[0][:72],
                author=commit.author.name,
                author_email=commit.author.email,
                date=commit.committed_datetime,
                files_changed=stats.get("files", 0),
                insertions=stats.get("insertions", 0),
                deletions=stats.get("deletions", 0),
            )
        )

    return commits


def get_commit_frequency(
    path: str | Path,
    days: int = 30,
) -> dict[str, int]:
    """Get commit frequency by day of week."""
    repo = get_repo(path)
    frequency: dict[str, int] = {
        "Monday": 0,
        "Tuesday": 0,
        "Wednesday": 0,
        "Thursday": 0,
        "Friday": 0,
        "Saturday": 0,
        "Sunday": 0,
    }

    cutoff = datetime.now(timezone.utc).timestamp() - (days * 24 * 60 * 60)

    for commit in repo.iter_commits():
        if commit.committed_date < cutoff:
            break
        day = commit.committed_datetime.strftime("%A")
        frequency[day] += 1

    return frequency


def get_file_types(path: str | Path) -> dict[str, int]:
    """Get count of files by extension in the repository."""
    repo = get_repo(path)
    extensions: Counter[str] = Counter()

    try:
        for item in repo.head.commit.tree.traverse():
            if item.type == "blob":
                ext = Path(item.path).suffix or "(no extension)"
                extensions[ext] += 1
    except (GitCommandError, ValueError):
        pass

    return dict(extensions.most_common(20))
