"""
Unit tests for main.py
"""

import pytest

from .main import create_command, parse_args
from .commands.analyze import AnalyzeCommand
from .commands.fix import FixCommand
from .commands.list import ListCommand


def test_parse_args_empty():
    """Empty arguments should throw error"""
    with pytest.raises(SystemExit):
        parse_args(args=[])


def test_parse_args_list_minimal():
    """Minimal list command parse"""
    result = parse_args(args=["list", "-u", "jdoe", "-t", "secret"])
    assert result.username == "jdoe"
    assert result.token == "secret"
    assert result.subparser_name == "list"


def test_parse_args_list_archived():
    """Tests the archived flag"""
    result = parse_args(args=["list", "-u", "jdoe", "-t", "secret"])
    assert result.archived == "deny"
    for valid_option in ["allow", "deny", "only"]:
        result = parse_args(
            args=["list", "-u", "jdoe", "-t", "secret", "--archived", valid_option]
        )
        assert result.archived == valid_option
    with pytest.raises(SystemExit):
        parse_args(args=["list", "-u", "jdoe", "-t", "secret", "--archived", "oops"])


def test_parse_args_fix_minimal():
    """Minimal fix command parse"""
    result = parse_args(args=["fix", "-u", "x", "--token", "sesame"])
    assert result.username == "x"
    assert result.token == "sesame"
    assert result.subparser_name == "fix"


def test_parse_args_fix_with_config_file_short():
    """Tests the -c option is parsed"""
    result = parse_args(args=["fix", "-c", "config.json"])
    assert result.subparser_name == "fix"
    assert result.config_file == "config.json"


def test_parse_args_fix_with_config_file_long():
    """Tests the --config-file option is parsed"""
    result = parse_args(args=["fix", "--config-file", "config2.json"])
    assert result.subparser_name == "fix"
    assert result.config_file == "config2.json"


def test_create_command_list():
    """Create ListCommand"""
    args = parse_args(args=["list", "-u", "jdoe", "-t", "secret"])
    cmd = create_command(args)
    assert isinstance(cmd, ListCommand)


def test_create_command_fix():
    """Create FixCommand"""
    args = parse_args(args=["fix", "-u", "jdoe", "-t", "secret"])
    cmd = create_command(args)
    assert isinstance(cmd, FixCommand)


def test_create_command_analyze():
    """Create AnalyzeCommand"""
    args = parse_args(
        args=["analyze", "-u", "jdoe", "-t", "secret", "--since", "2021-11-06"]
    )
    cmd = create_command(args)
    assert isinstance(cmd, AnalyzeCommand)


def test_parse_args_fix_fixer_selection():
    """Parse specific fixers"""
    args = parse_args(
        args=["fix", "-u", "jdoe", "-t", "secret", "--only-fixers", "dotnet", "maven"]
    )
    assert args.only_fixers == ["dotnet", "maven"]
    args = parse_args(
        args=["fix", "-u", "jdoe", "-t", "secret", "--except-fixers", "dotnet", "vb6"]
    )
    assert args.except_fixers == ["dotnet", "vb6"]
    with pytest.raises(SystemExit):
        parse_args(
            args=[
                "fix",
                "-u",
                "jdoe",
                "-t",
                "secret",
                "--except-fixers",
                "foo",
                "--skip-fixers",
                "bar",
            ]
        )
