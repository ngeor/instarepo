from datetime import timedelta
from .github import Repo
from .repo_source import (
    StringFilter,
    FilterMode,
    filter_by_name_prefix,
    parse_timedelta,
)


def test_filter_by_repo_no_filter():
    repos = [dummy_repo("foo"), dummy_repo("bar")]
    result = list(filter_by_name_prefix(repos, None))
    assert result == repos


def test_filter_by_repo_allow_filter():
    repos = [dummy_repo("foo"), dummy_repo("bar")]
    string_filter = StringFilter("whatever", FilterMode.ALLOW)
    result = list(filter_by_name_prefix(repos, string_filter))
    assert result == repos


def test_filter_by_repo_only_filter():
    repos = [dummy_repo("foo"), dummy_repo("bar")]
    string_filter = StringFilter("f", FilterMode.ONLY)
    result = list(filter_by_name_prefix(repos, string_filter))
    assert result == repos[0:1]


def test_filter_by_repo_deny_filter():
    repos = [dummy_repo("foo"), dummy_repo("bar")]
    string_filter = StringFilter("f", FilterMode.DENY)
    result = list(filter_by_name_prefix(repos, string_filter))
    assert result == repos[1:]


def dummy_repo(name: str) -> Repo:
    return Repo(
        {
            "name": name,
            "archived": False,
            "clone_url": "",
            "html_url": "",
            "ssh_url": "",
            "default_branch": "",
            "full_name": "",
            "description": "",
            "private": False,
            "fork": False,
            "created_at": "2021-11-04T21:32:00Z",
            "pushed_at": "2021-11-04T21:32:00Z",
            "updated_at": "2021-11-04T21:32:00Z",
            "language": "",
        }
    )


def test_parse_timedelta():
    assert parse_timedelta("4h") == timedelta(hours=4)
    assert parse_timedelta("15m") == timedelta(minutes=15)
    assert parse_timedelta("3d") == timedelta(days=3)
    assert parse_timedelta(None) is None
