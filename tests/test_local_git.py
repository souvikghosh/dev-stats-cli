"""Tests for local git module."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

from src.dev_stats_cli.local_git import (
    CommitInfo,
    LocalRepoStats,
    LocalGitError,
    get_repo,
)


class TestGetRepo:
    def test_invalid_path(self, tmp_path):
        with pytest.raises(LocalGitError, match="Not a git repository"):
            get_repo(tmp_path)

    def test_valid_repo(self, tmp_path):
        # Create a git repo
        import subprocess
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)

        repo = get_repo(tmp_path)
        assert repo is not None


class TestCommitInfo:
    def test_creation(self):
        commit = CommitInfo(
            sha="abc1234",
            message="Test commit",
            author="Test Author",
            author_email="test@example.com",
            date=datetime.now(timezone.utc),
            files_changed=5,
            insertions=100,
            deletions=50,
        )
        assert commit.sha == "abc1234"
        assert commit.message == "Test commit"
        assert commit.files_changed == 5


class TestLocalRepoStats:
    def test_creation(self):
        stats = LocalRepoStats(
            path="/path/to/repo",
            name="repo",
            current_branch="main",
            total_commits=100,
            total_branches=3,
            contributors=[("Alice", 50), ("Bob", 30)],
            first_commit=datetime(2023, 1, 1, tzinfo=timezone.utc),
            last_commit=datetime(2024, 1, 1, tzinfo=timezone.utc),
            total_lines_added=5000,
            total_lines_deleted=2000,
        )
        assert stats.name == "repo"
        assert stats.total_commits == 100
        assert len(stats.contributors) == 2
