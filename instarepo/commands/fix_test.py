import os
from .fix import format_body


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
