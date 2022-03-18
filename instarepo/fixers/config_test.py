"""Unit tests for config.py"""

from .config import PartialConfig


def test_empty_config():
    config = PartialConfig({})
    assert config.get_setting("ngeor/instarepo", "enabled") is None


def test_missing_repo():
    config = PartialConfig({"defaults": {"enabled": True}})
    assert config.get_setting("ngeor/instarepo", "enabled")


def test_present_repo():
    config = PartialConfig(
        {
            "defaults": {"enabled": True},
            "repos": {"ngeor/instarepo": {"enabled": False}},
        }
    )
    assert not config.get_setting("ngeor/instarepo", "enabled")


def test_nested_key():
    config = PartialConfig(
        {
            "defaults": {"editor": {"overwrite": {True}}},
            "repos": {"ngeor/instarepo": {"enabled": False}},
        }
    )
    assert config.get_setting("ngeor/instarepo", "editor", "overwrite")
