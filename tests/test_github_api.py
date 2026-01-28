"""Tests for GitHub API module."""

import pytest

from src.dev_stats_cli.github_api import (
    RepoStats,
    calculate_language_stats,
    calculate_summary_stats,
)
from datetime import datetime, timezone


@pytest.fixture
def sample_repos():
    """Sample repository data for testing."""
    return [
        RepoStats(
            name="repo1",
            full_name="user/repo1",
            description="Test repo 1",
            language="Python",
            stars=100,
            forks=20,
            watchers=100,
            open_issues=5,
            created_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
            updated_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
            is_fork=False,
            size_kb=1024,
        ),
        RepoStats(
            name="repo2",
            full_name="user/repo2",
            description="Test repo 2",
            language="Python",
            stars=50,
            forks=10,
            watchers=50,
            open_issues=2,
            created_at=datetime(2023, 6, 1, tzinfo=timezone.utc),
            updated_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
            is_fork=False,
            size_kb=512,
        ),
        RepoStats(
            name="repo3",
            full_name="user/repo3",
            description="Test repo 3",
            language="JavaScript",
            stars=25,
            forks=5,
            watchers=25,
            open_issues=1,
            created_at=datetime(2023, 9, 1, tzinfo=timezone.utc),
            updated_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
            is_fork=False,
            size_kb=256,
        ),
    ]


class TestCalculateLanguageStats:
    def test_counts_languages(self, sample_repos):
        stats = calculate_language_stats(sample_repos)
        assert stats["Python"] == 2
        assert stats["JavaScript"] == 1

    def test_sorted_by_count(self, sample_repos):
        stats = calculate_language_stats(sample_repos)
        counts = list(stats.values())
        assert counts == sorted(counts, reverse=True)

    def test_empty_repos(self):
        stats = calculate_language_stats([])
        assert stats == {}


class TestCalculateSummaryStats:
    def test_total_repos(self, sample_repos):
        stats = calculate_summary_stats(sample_repos)
        assert stats["total_repos"] == 3

    def test_total_stars(self, sample_repos):
        stats = calculate_summary_stats(sample_repos)
        assert stats["total_stars"] == 175

    def test_total_forks(self, sample_repos):
        stats = calculate_summary_stats(sample_repos)
        assert stats["total_forks"] == 35

    def test_average_stars(self, sample_repos):
        stats = calculate_summary_stats(sample_repos)
        assert stats["average_stars"] == pytest.approx(58.3, 0.1)

    def test_total_size(self, sample_repos):
        stats = calculate_summary_stats(sample_repos)
        # (1024 + 512 + 256) / 1024 = 1.75 MB
        assert stats["total_size_mb"] == 1.75

    def test_top_language(self, sample_repos):
        stats = calculate_summary_stats(sample_repos)
        assert stats["top_language"] == "Python"

    def test_empty_repos(self):
        stats = calculate_summary_stats([])
        assert stats["total_repos"] == 0
        assert stats["total_stars"] == 0
        assert stats["average_stars"] == 0
        assert stats["top_language"] is None
