"""Unit tests for fix.py"""
import os
import pytest
from instarepo.fixers.dotnet import MustHaveCSharpAppVeyor
from .fix import format_body, all_fixer_classes, fixer_class_to_fixer_key


def test_format_body_one_change():
    changes = ["Simple change"]
    expected_body = """The following fixes have been applied:
- Simple change
""".replace(
        os.linesep, "\n"
    )
    actual_body = format_body(changes)
    assert actual_body == expected_body


def test_format_body_two_changes():
    changes = ["Simple change", "Second change"]
    expected_body = """The following fixes have been applied:
- Simple change
- Second change
""".replace(
        os.linesep, "\n"
    )
    actual_body = format_body(changes)
    assert actual_body == expected_body


def test_format_body_convert_multi_line_to_indentation():
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


def test_fixer_has_doc_string(fixer_class):
    """Tests all fixer classes have a doc string"""
    assert fixer_class
    assert fixer_class.__doc__


def test_fixer_class_to_fixer_key():
    """Tests various fixer classes can be mapped to a key"""
    assert (
        fixer_class_to_fixer_key(MustHaveCSharpAppVeyor)
        == "dotnet.must_have_c_sharp_app_veyor"
    )


def test_can_create_fixer(fixer_class):
    """Tests that it is possible to instantiate all fixers"""
    mock_git = ()
    mock_github = ()
    mock_repo = ()
    instance = fixer_class(git=mock_git, repo=mock_repo, github=mock_github)
    assert instance
