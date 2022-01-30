"""Unit tests for fix.py"""
import os
import pytest
import instarepo.fixers.dotnet
import instarepo.fixers.maven
from .fix import (
    format_body,
    all_fixer_classes,
    fixer_class_to_fixer_key,
    select_fixer_classes,
)
import instarepo.git


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
        fixer_class_to_fixer_key(instarepo.fixers.dotnet.MustHaveCSharpAppVeyorFix)
        == "dotnet.must_have_c_sharp_app_veyor"
    )


def test_can_create_fixer(fixer_class):  # pylint: disable=redefined-outer-name
    """Tests that it is possible to instantiate all fixers"""
    mock_git = instarepo.git.GitWorkingDir("/tmp")
    mock_github = ()
    mock_repo = ()
    instance = fixer_class(
        git=mock_git, repo=mock_repo, github=mock_github, verbose=False
    )
    assert instance


def test_select_fixer_classes():
    """Tests the select_fixer_classes function"""
    assert list(all_fixer_classes()) == list(select_fixer_classes())
    assert [
        instarepo.fixers.dotnet.DotNetFrameworkVersionFix,
        instarepo.fixers.dotnet.MustHaveCSharpAppVeyorFix,
    ] == list(select_fixer_classes(only_fixers=["dotnet"]))
    assert [
        instarepo.fixers.dotnet.DotNetFrameworkVersionFix,
        instarepo.fixers.dotnet.MustHaveCSharpAppVeyorFix,
        instarepo.fixers.maven.MavenFix,
        instarepo.fixers.maven.MustHaveMavenGitHubWorkflowFix,
        instarepo.fixers.maven.MavenBadgesFix,
        instarepo.fixers.maven.UrlFix,
    ] == list(select_fixer_classes(only_fixers=["dotnet", "maven"]))
    with pytest.raises(ValueError):
        list(select_fixer_classes(only_fixers=["a"], except_fixers=["b"]))
    assert [
        instarepo.fixers.dotnet.DotNetFrameworkVersionFix,
        instarepo.fixers.dotnet.MustHaveCSharpAppVeyorFix,
    ] == list(
        select_fixer_classes(
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
    )
