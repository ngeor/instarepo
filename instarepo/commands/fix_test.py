"""Unit tests for fix.py"""
import os

import instarepo.fixers.base
import instarepo.fixers.changelog
import instarepo.fixers.config
import instarepo.fixers.context
import instarepo.fixers.dotnet
import instarepo.fixers.maven
import instarepo.git

from .fix import (
    create_composite_fixer,
    format_body,
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
