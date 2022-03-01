"""Unit tests for fix.py"""
import collections
import os

import pytest

import instarepo.fixers.base
import instarepo.fixers.changelog
import instarepo.fixers.config
import instarepo.fixers.context
import instarepo.fixers.dotnet
import instarepo.fixers.maven
import instarepo.git

from .fix import (
    all_fixer_classes,
    classes_in_module,
    create_composite_fixer,
    fixer_class_to_fixer_key,
    format_body,
    select_fixer_classes,
    try_get_fixer_order,
)


class TestFormatBody:
    """Unit tests for format_body"""

    def test_one_change(self):
        changes = ["Simple change"]
        expected_body = """The following fixes have been applied:
- Simple change
""".replace(
            os.linesep, "\n"
        )
        actual_body = format_body(changes)
        assert actual_body == expected_body

    def test_two_changes(self):
        changes = ["Simple change", "Second change"]
        expected_body = """The following fixes have been applied:
- Simple change
- Second change
""".replace(
            os.linesep, "\n"
        )
        actual_body = format_body(changes)
        assert actual_body == expected_body

    def test_convert_multi_line_to_indentation(self):
        changes = [
            """Complex change
Updated parent to 1.0
"""
        ]
        expected_body = """The following fixes have been applied:
- Complex change
  Updated parent to 1.0
""".replace(
            os.linesep, "\n"
        )
        actual_body = format_body(changes)
        assert actual_body == expected_body


@pytest.fixture(params=[clz for clz in all_fixer_classes()])
def fixer_class(request):
    return request.param


def test_fixer_has_doc_string(fixer_class):  # pylint: disable=redefined-outer-name
    """Tests all fixer classes have a doc string"""
    assert fixer_class
    assert fixer_class.__doc__


def test_fixer_class_to_fixer_key():
    """Tests various fixer classes can be mapped to a key"""
    assert (
        fixer_class_to_fixer_key(instarepo.fixers.dotnet.MustHaveCIFix)
        == "dotnet.must_have_ci"
    )
    assert fixer_class_to_fixer_key(instarepo.fixers.maven.UrlFix) == "maven.url"


def test_can_create_fixer(fixer_class):  # pylint: disable=redefined-outer-name
    """Tests that it is possible to instantiate all fixers"""
    mock_git = instarepo.git.GitWorkingDir("/tmp")
    mock_config = instarepo.fixers.config.PartialConfig({})
    mock_github = ()
    repo_type = collections.namedtuple("Repo", ["full_name"])
    mock_repo = repo_type("ngeor/test")
    instance = fixer_class(
        instarepo.fixers.context.Context(
            git=mock_git,
            config=mock_config,
            repo=mock_repo,
            github=mock_github,
            verbose=False,
        )
    )
    assert instance


def test_can_create_fixer_for_local_dir(
    fixer_class,
):  # pylint: disable=redefined-outer-name
    """Tests that it is possible to instantiate all fixers without repo/github instances"""
    mock_git = instarepo.git.GitWorkingDir("/tmp")
    mock_config = instarepo.fixers.config.PartialConfig({})
    instance = fixer_class(
        instarepo.fixers.context.Context(
            git=mock_git, config=mock_config, repo=None, github=None, verbose=False
        )
    )
    assert instance


class TestSelectFixerClasses:
    def test_returns_all_when_unfiltered(self):
        assert len(list(all_fixer_classes())) == len(select_fixer_classes())

    def test_filter_by_name(self):
        assert [
            instarepo.fixers.dotnet.MustHaveCIFix,
        ] == select_fixer_classes(only_fixers=["dotnet"])

    def test_filter_by_two_names(self):
        assert [
            instarepo.fixers.dotnet.MustHaveCIFix,
            instarepo.fixers.maven.MustHaveCIFix,
            instarepo.fixers.maven.MavenBadgesFix,
            instarepo.fixers.maven.UrlFix,
        ] == select_fixer_classes(only_fixers=["dotnet", "maven"])

    def test_cannot_use_only_and_except_together(self):
        with pytest.raises(ValueError):
            select_fixer_classes(only_fixers=["a"], except_fixers=["b"])

    def test_filter_except(self):
        assert [instarepo.fixers.dotnet.MustHaveCIFix,] == select_fixer_classes(
            except_fixers=[
                "changelog",
                "ci",
                "license",
                "maven",
                "missing_files",
                "pascal",
                "r",
                "vb",
            ]
        )

    def test_sort(self):
        assert [
            instarepo.fixers.changelog.MustHaveCliffTomlFix,
            instarepo.fixers.dotnet.MustHaveCIFix,
        ] == select_fixer_classes(only_fixers=["dotnet", "changelog"])


def test_classes_in_module():
    assert [instarepo.git.GitWorkingDir] == list(classes_in_module(instarepo.git))


def test_try_get_fix_order():
    assert try_get_fixer_order(instarepo.fixers.dotnet.MustHaveCIFix) == 0
    assert try_get_fixer_order(instarepo.fixers.changelog.MustHaveCliffTomlFix) == -100


def test_create_composite_fixer():
    # arrange
    context = instarepo.fixers.context.Context(git=None, config=None)
    fixer_classes = [
        instarepo.fixers.changelog.MustHaveCliffTomlFix,
    ]
    # act
    composite_fixer = create_composite_fixer(fixer_classes, context)
    # assert
    assert composite_fixer
    assert isinstance(composite_fixer, instarepo.fixers.base.CompositeFix)
    assert composite_fixer.rules
    assert isinstance(
        composite_fixer.rules[0], instarepo.fixers.changelog.MustHaveCliffTomlFix
    )
