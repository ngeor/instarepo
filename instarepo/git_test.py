"""
Unit tests for the git module.
"""
import collections
import subprocess
from pytest_mock import MockerFixture
import instarepo.git


def test_clone(mocker: MockerFixture):
    # arrange
    mock = mocker.patch("subprocess.run")

    # act
    result = instarepo.git.clone("ssh://hello.git", "/tmp/hello")

    # assert
    mock.assert_called_once_with(
        ["git", "clone", "ssh://hello.git", "/tmp/hello"], check=True
    )
    assert result.dir == "/tmp/hello"


def test_clone_quietly(mocker: MockerFixture):
    # arrange
    mock = mocker.patch("subprocess.run")

    # act
    result = instarepo.git.clone("ssh://hello.git", "/tmp/hello", quiet=True)

    # assert
    mock.assert_called_once_with(
        ["git", "clone", "-q", "ssh://hello.git", "/tmp/hello"], check=True
    )
    assert result.dir == "/tmp/hello"


def test_create_branch(mocker: MockerFixture):
    # arrange
    mock = mocker.patch("subprocess.run")
    git = instarepo.git.GitWorkingDir("/tmp/hello")

    # act
    git.create_branch("release")

    # assert
    mock.assert_called_once_with(
        ["git", "checkout", "-b", "release"], check=True, cwd="/tmp/hello"
    )


def test_create_branch_quietly(mocker: MockerFixture):
    # arrange
    mock = mocker.patch("subprocess.run")
    git = instarepo.git.GitWorkingDir("/tmp/hello", quiet=True)

    # act
    git.create_branch("release")

    # assert
    mock.assert_called_once_with(
        ["git", "checkout", "-q", "-b", "release"], check=True, cwd="/tmp/hello"
    )


def test_add(mocker: MockerFixture):
    # arrange
    mock = mocker.patch("subprocess.run")
    git = instarepo.git.GitWorkingDir("/tmp/hello")

    # act
    git.add("test.txt")

    # assert
    mock.assert_called_once_with(
        ["git", "add", "test.txt"], check=True, cwd="/tmp/hello"
    )


def test_commit(mocker: MockerFixture):
    # arrange
    mock = mocker.patch("subprocess.run")
    git = instarepo.git.GitWorkingDir("/tmp/hello")

    # act
    git.commit("oops")

    # assert
    mock.assert_called_once_with(
        ["git", "commit", "-m", "oops"], check=True, cwd="/tmp/hello"
    )


def test_commit_quietly(mocker: MockerFixture):
    # arrange
    mock = mocker.patch("subprocess.run")
    git = instarepo.git.GitWorkingDir("/tmp/hello", quiet=True)

    # act
    git.commit("oops")

    # assert
    mock.assert_called_once_with(
        ["git", "commit", "-q", "-m", "oops"], check=True, cwd="/tmp/hello"
    )


def test_push(mocker: MockerFixture):
    # arrange
    mock = mocker.patch("subprocess.run")
    git = instarepo.git.GitWorkingDir("/tmp/hello")

    # act
    git.push()

    # assert
    mock.assert_called_once_with(
        ["git", "push", "-u", "origin", "HEAD"],
        check=True,
        cwd="/tmp/hello",
    )


def test_delete_remote_branch(mocker: MockerFixture):
    # arrange
    mock = mocker.patch("subprocess.run")
    git = instarepo.git.GitWorkingDir("/tmp/hello")

    # act
    git.delete_remote_branch("obsolete-branch")

    # assert
    mock.assert_called_once_with(
        ["git", "push", "--delete", "origin", "obsolete-branch"],
        check=True,
        cwd="/tmp/hello",
    )


def test_join():
    git = instarepo.git.GitWorkingDir("/tmp/hello")
    filename = git.join("src", "index.js").replace("\\", "/")
    assert filename == "/tmp/hello/src/index.js"


def test_join_with_slashes_in_string():
    git = instarepo.git.GitWorkingDir("/tmp/hello")
    filename = git.join("src/index.js").replace("\\", "/")
    assert filename == "/tmp/hello/src/index.js"


def test_is_remote_branch_present(mocker: MockerFixture):
    # arrange
    result_type = collections.namedtuple("ProcessResult", ["stdout"])
    result = result_type("remote-ref")
    mock = mocker.patch("subprocess.run")
    mock.return_value = result
    git = instarepo.git.GitWorkingDir("/tmp/hello")

    # act
    result = git.is_remote_branch_present("existing-branch")

    # assert
    mock.assert_called_once_with(
        ["git", "rev-parse", "-q", "--verify", "remotes/origin/existing-branch"],
        check=True,
        cwd="/tmp/hello",
        encoding="utf-8",
        stdout=subprocess.PIPE,
    )
    assert result


def test_is_remote_branch_absent(mocker: MockerFixture):
    # arrange
    result_type = collections.namedtuple("ProcessResult", ["stdout"])
    result = result_type("")
    mock = mocker.patch("subprocess.run")
    mock.return_value = result
    git = instarepo.git.GitWorkingDir("/tmp/hello")

    # act
    result = git.is_remote_branch_present("missing-branch")

    # assert
    mock.assert_called_once_with(
        ["git", "rev-parse", "-q", "--verify", "remotes/origin/missing-branch"],
        check=True,
        cwd="/tmp/hello",
        encoding="utf-8",
        stdout=subprocess.PIPE,
    )
    assert not result


def test_get_remote_url(mocker: MockerFixture):
    # arrange
    result_type = collections.namedtuple("ProcessResult", ["stdout"])
    result = result_type("git@github.com:ngeor/instarepo.git\n")
    mock = mocker.patch("subprocess.run")
    mock.return_value = result
    git = instarepo.git.GitWorkingDir("/tmp/hello")

    # act
    result = git.get_remote_url()

    # assert
    mock.assert_called_once_with(
        ["git", "remote", "get-url", "origin"],
        check=True,
        cwd="/tmp/hello",
        encoding="utf-8",
        stdout=subprocess.PIPE,
    )
    assert result == "git@github.com:ngeor/instarepo.git"


def test_get_default_branch(mocker: MockerFixture):
    # arrange
    result_type = collections.namedtuple("ProcessResult", ["stdout"])
    result = result_type("refs/remotes/origin/trunk\n")
    mock = mocker.patch("subprocess.run")
    mock.return_value = result
    git = instarepo.git.GitWorkingDir("/tmp/hello")

    # act
    result = git.get_default_branch()

    # assert
    mock.assert_called_once_with(
        ["git", "symbolic-ref", "refs/remotes/origin/HEAD"],
        check=True,
        cwd="/tmp/hello",
        encoding="utf-8",
        stdout=subprocess.PIPE,
    )
    assert result == "trunk"
