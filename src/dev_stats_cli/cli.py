"""CLI commands using Typer."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from . import github_api, local_git

app = typer.Typer(
    name="devstats",
    help="Developer statistics CLI - GitHub & local git analysis",
    add_completion=False,
)
console = Console()


@app.command()
def github(
    username: str = typer.Argument(..., help="GitHub username"),
    token: Optional[str] = typer.Option(
        None,
        "--token",
        "-t",
        envvar="GITHUB_TOKEN",
        help="GitHub personal access token",
    ),
    include_forks: bool = typer.Option(
        False,
        "--forks",
        "-f",
        help="Include forked repositories",
    ),
):
    """Show GitHub profile and repository statistics."""
    try:
        with console.status(f"Fetching data for {username}..."):
            user = github_api.get_user(username, token)
            repos = github_api.get_user_repos(username, token, include_forks)
            summary = github_api.calculate_summary_stats(repos)

        # User profile panel
        profile_text = Text()
        profile_text.append(f"{user.name or user.username}\n", style="bold cyan")
        if user.bio:
            profile_text.append(f"{user.bio}\n", style="dim")
        profile_text.append(f"\nPublic Repos: {user.public_repos}  ")
        profile_text.append(f"Followers: {user.followers}  ")
        profile_text.append(f"Following: {user.following}")

        console.print(Panel(profile_text, title=f"@{user.username}", border_style="blue"))

        # Summary statistics
        stats_table = Table(title="Repository Statistics", show_header=False)
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="green")

        stats_table.add_row("Total Repositories", str(summary["total_repos"]))
        stats_table.add_row("Total Stars", f"{summary['total_stars']:,}")
        stats_table.add_row("Total Forks", f"{summary['total_forks']:,}")
        stats_table.add_row("Average Stars/Repo", str(summary["average_stars"]))
        stats_table.add_row("Total Size", f"{summary['total_size_mb']} MB")
        stats_table.add_row("Top Language", summary["top_language"] or "N/A")

        console.print(stats_table)

        # Language breakdown
        if summary["languages"]:
            lang_table = Table(title="Languages Used")
            lang_table.add_column("Language", style="cyan")
            lang_table.add_column("Repos", style="green", justify="right")
            lang_table.add_column("Bar", style="yellow")

            max_count = max(summary["languages"].values())
            for lang, count in list(summary["languages"].items())[:10]:
                bar_width = int((count / max_count) * 20)
                bar = "" * bar_width
                lang_table.add_row(lang, str(count), bar)

            console.print(lang_table)

        # Top repositories
        if repos:
            repo_table = Table(title="Top Repositories (by stars)")
            repo_table.add_column("Repository", style="cyan")
            repo_table.add_column("Stars", style="yellow", justify="right")
            repo_table.add_column("Forks", style="blue", justify="right")
            repo_table.add_column("Language", style="green")

            sorted_repos = sorted(repos, key=lambda r: r.stars, reverse=True)[:10]
            for repo in sorted_repos:
                repo_table.add_row(
                    repo.name,
                    str(repo.stars),
                    str(repo.forks),
                    repo.language or "-",
                )

            console.print(repo_table)

    except github_api.GitHubError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def local(
    path: Path = typer.Argument(
        ".",
        help="Path to git repository",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    commits: int = typer.Option(
        10,
        "--commits",
        "-c",
        help="Number of recent commits to show",
    ),
):
    """Analyze a local git repository."""
    try:
        with console.status(f"Analyzing repository..."):
            stats = local_git.analyze_repo(path)
            recent = local_git.get_recent_commits(path, commits)
            frequency = local_git.get_commit_frequency(path)
            file_types = local_git.get_file_types(path)

        # Repository info panel
        info_text = Text()
        info_text.append(f"Path: {stats.path}\n", style="dim")
        info_text.append(f"Branch: {stats.current_branch}\n", style="cyan")
        info_text.append(f"Commits: {stats.total_commits:,}  ")
        info_text.append(f"Branches: {stats.total_branches}")

        if stats.first_commit and stats.last_commit:
            info_text.append(f"\nFirst commit: {stats.first_commit.strftime('%Y-%m-%d')}")
            info_text.append(f"\nLast commit: {stats.last_commit.strftime('%Y-%m-%d')}")

        console.print(Panel(info_text, title=stats.name, border_style="blue"))

        # Line changes
        changes_text = Text()
        changes_text.append(f"+{stats.total_lines_added:,}", style="green")
        changes_text.append(" / ")
        changes_text.append(f"-{stats.total_lines_deleted:,}", style="red")
        changes_text.append(" lines (recent commits)")
        console.print(changes_text)

        # Contributors
        if stats.contributors:
            contrib_table = Table(title="Top Contributors")
            contrib_table.add_column("Author", style="cyan")
            contrib_table.add_column("Commits", style="green", justify="right")
            contrib_table.add_column("Bar", style="yellow")

            max_commits = stats.contributors[0][1] if stats.contributors else 1
            for author, count in stats.contributors[:5]:
                bar_width = int((count / max_commits) * 20)
                bar = "" * bar_width
                contrib_table.add_row(author, str(count), bar)

            console.print(contrib_table)

        # Commit frequency
        freq_table = Table(title="Commit Frequency (last 30 days)")
        freq_table.add_column("Day", style="cyan")
        freq_table.add_column("Commits", style="green", justify="right")
        freq_table.add_column("Activity", style="yellow")

        max_freq = max(frequency.values()) if any(frequency.values()) else 1
        for day, count in frequency.items():
            bar_width = int((count / max_freq) * 15) if max_freq > 0 else 0
            bar = "" * bar_width if count > 0 else ""
            freq_table.add_row(day[:3], str(count), bar)

        console.print(freq_table)

        # File types
        if file_types:
            files_table = Table(title="File Types")
            files_table.add_column("Extension", style="cyan")
            files_table.add_column("Count", style="green", justify="right")

            for ext, count in list(file_types.items())[:10]:
                files_table.add_row(ext, str(count))

            console.print(files_table)

        # Recent commits
        if recent:
            commits_table = Table(title=f"Recent Commits ({len(recent)})")
            commits_table.add_column("SHA", style="yellow", width=7)
            commits_table.add_column("Message", style="white")
            commits_table.add_column("Author", style="cyan")
            commits_table.add_column("Changes", style="dim")

            for commit in recent:
                changes = f"+{commit.insertions}/-{commit.deletions}"
                commits_table.add_row(
                    commit.sha,
                    commit.message[:50],
                    commit.author,
                    changes,
                )

            console.print(commits_table)

    except local_git.LocalGitError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def compare(
    username1: str = typer.Argument(..., help="First GitHub username"),
    username2: str = typer.Argument(..., help="Second GitHub username"),
    token: Optional[str] = typer.Option(
        None,
        "--token",
        "-t",
        envvar="GITHUB_TOKEN",
        help="GitHub personal access token",
    ),
):
    """Compare two GitHub profiles."""
    try:
        with console.status("Fetching data..."):
            user1 = github_api.get_user(username1, token)
            user2 = github_api.get_user(username2, token)
            repos1 = github_api.get_user_repos(username1, token)
            repos2 = github_api.get_user_repos(username2, token)
            stats1 = github_api.calculate_summary_stats(repos1)
            stats2 = github_api.calculate_summary_stats(repos2)

        # Comparison table
        table = Table(title=f"Comparison: {username1} vs {username2}")
        table.add_column("Metric", style="cyan")
        table.add_column(username1, style="green", justify="right")
        table.add_column(username2, style="yellow", justify="right")
        table.add_column("Winner", style="bold")

        metrics = [
            ("Followers", user1.followers, user2.followers),
            ("Public Repos", user1.public_repos, user2.public_repos),
            ("Total Stars", stats1["total_stars"], stats2["total_stars"]),
            ("Total Forks", stats1["total_forks"], stats2["total_forks"]),
            ("Avg Stars/Repo", stats1["average_stars"], stats2["average_stars"]),
        ]

        for metric, val1, val2 in metrics:
            if val1 > val2:
                winner = username1
            elif val2 > val1:
                winner = username2
            else:
                winner = "Tie"

            table.add_row(metric, str(val1), str(val2), winner)

        console.print(table)

    except github_api.GitHubError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def version():
    """Show version information."""
    from . import __version__

    console.print(f"devstats version {__version__}")


if __name__ == "__main__":
    app()
