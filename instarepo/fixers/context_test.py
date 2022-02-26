"""Unit tests for the context module"""

import collections
from pytest_mock import MockerFixture
from .config import PartialConfig
from .context import Context
from ..git import GitWorkingDir


def test_full_name_from_repo():
    git = ()
    config = PartialConfig({})
    repo_type = collections.namedtuple("Repo", "full_name")
    repo = repo_type("ngeor/test")
    context = Context(git, config, repo, github=None, verbose=False)
    assert context.full_name() == "ngeor/test"


def test_full_name_from_git_remote(mocker: MockerFixture):
    git = GitWorkingDir("/tmp")
    mock = mocker.patch.object(git, "get_remote_url")
    mock.return_value = "git@github.com:foo/bar.git"
    config = PartialConfig({})
    context = Context(git, config, repo=None, github=None, verbose=False)
    assert context.full_name() == "foo/bar"
