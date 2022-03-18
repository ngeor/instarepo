"""Unit tests for missing_files.py"""

import os.path
import tempfile
from pytest_mock import MockerFixture
import instarepo.fixers.config
import instarepo.fixers.context
from .missing_files import MustHaveEditorConfigFix, EDITOR_CONFIG
from ..git import GitWorkingDir


def test_editor_config(mocker: MockerFixture):
    with tempfile.TemporaryDirectory() as tmp_dir:
        # arrange
        filename = os.path.join(tmp_dir, ".editorconfig")
        git = GitWorkingDir(tmp_dir, quiet=True)
        git_add = mocker.patch.object(git, "add")
        git_commit = mocker.patch.object(git, "commit")
        config = instarepo.fixers.config.PartialConfig({})
        context = instarepo.fixers.context.Context(git, config)
        fixer = MustHaveEditorConfigFix(context)

        # act
        result = fixer.run()

        # assert
        assert result == ["chore: Adding .editorconfig"]
        assert os.path.isfile(os.path.join(tmp_dir, ".editorconfig"))
        with open(filename, "r", encoding="utf-8") as file:
            assert file.read() == EDITOR_CONFIG
        git_add.assert_called_once_with(".editorconfig")
        git_commit.assert_called_once_with("chore: Adding .editorconfig")


def test_editor_config_already_exists(mocker: MockerFixture):
    with tempfile.TemporaryDirectory() as tmp_dir:
        # arrange
        filename = os.path.join(tmp_dir, ".editorconfig")
        with open(filename, "w", encoding="utf-8") as file:
            file.write("# hello world")
        git = GitWorkingDir(tmp_dir, quiet=True)
        git_add = mocker.patch.object(git, "add")
        git_commit = mocker.patch.object(git, "commit")
        git_get_remote_url = mocker.patch.object(git, "get_remote_url")
        git_get_remote_url.return_value = "git@github.com:ngeor/instarepo.git"
        config = instarepo.fixers.config.PartialConfig({})
        context = instarepo.fixers.context.Context(git, config)
        fixer = MustHaveEditorConfigFix(context)

        # act
        result = fixer.run()

        # assert
        assert result == []
        assert os.path.isfile(os.path.join(tmp_dir, ".editorconfig"))
        with open(filename, "r", encoding="utf-8") as file:
            assert file.read() == "# hello world"
        git_add.assert_not_called()
        git_commit.assert_not_called()


def test_editor_config_already_exists_overwrite(mocker: MockerFixture):
    with tempfile.TemporaryDirectory() as tmp_dir:
        # arrange
        filename = os.path.join(tmp_dir, ".editorconfig")
        with open(filename, "w", encoding="utf-8") as file:
            file.write("# hello world")
        git = GitWorkingDir(tmp_dir, quiet=True)
        git_add = mocker.patch.object(git, "add")
        git_commit = mocker.patch.object(git, "commit")
        git_get_remote_url = mocker.patch.object(git, "get_remote_url")
        git_get_remote_url.return_value = "git@github.com:ngeor/instarepo.git"
        config = instarepo.fixers.config.PartialConfig(
            {"defaults": {"missing_files.must_have_editor_config": {"overwrite": True}}}
        )
        context = instarepo.fixers.context.Context(git, config)
        fixer = MustHaveEditorConfigFix(context)

        # act
        result = fixer.run()

        # assert
        assert result == ["chore: Updated .editorconfig"]
        assert os.path.isfile(os.path.join(tmp_dir, ".editorconfig"))
        with open(filename, "r", encoding="utf-8") as file:
            assert file.read() == EDITOR_CONFIG
        git_add.assert_called_once_with(".editorconfig")
        git_commit.assert_called_once_with("chore: Updated .editorconfig")


def test_editor_config_already_exists_matching_template(mocker: MockerFixture):
    with tempfile.TemporaryDirectory() as tmp_dir:
        # arrange
        filename = os.path.join(tmp_dir, ".editorconfig")
        with open(filename, "w", encoding="utf-8") as file:
            file.write(EDITOR_CONFIG)
        git = GitWorkingDir(tmp_dir, quiet=True)
        git_add = mocker.patch.object(git, "add")
        git_commit = mocker.patch.object(git, "commit")
        git_get_remote_url = mocker.patch.object(git, "get_remote_url")
        git_get_remote_url.return_value = "git@github.com:ngeor/instarepo.git"
        config = instarepo.fixers.config.PartialConfig(
            {"defaults": {"missing_files.must_have_editor_config": {"overwrite": True}}}
        )
        context = instarepo.fixers.context.Context(git, config)
        fixer = MustHaveEditorConfigFix(context)

        # act
        result = fixer.run()

        # assert
        assert result == []
        assert os.path.isfile(os.path.join(tmp_dir, ".editorconfig"))
        with open(filename, "r", encoding="utf-8") as file:
            assert file.read() == EDITOR_CONFIG
        git_add.assert_not_called()
        git_commit.assert_not_called()
