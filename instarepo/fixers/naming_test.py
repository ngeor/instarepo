"""Unit tests for naming.py"""

import instarepo.fixers.dotnet
import instarepo.fixers.maven

from .naming import fixer_class_to_fixer_key


def test_fixer_class_to_fixer_key():
    """Tests various fixer classes can be mapped to a key"""
    assert (
        fixer_class_to_fixer_key(instarepo.fixers.dotnet.MustHaveCIFix)
        == "dotnet.must_have_ci"
    )
    assert fixer_class_to_fixer_key(instarepo.fixers.maven.UrlFix) == "maven.url"
