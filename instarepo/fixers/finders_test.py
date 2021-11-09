"""Unit tests for finders.py"""

from .finders import is_file_of_extension


class TestIsFileOfExtension:
    """Unit tests for is_file_of_extension"""

    def test_directory(self):
        entry = MockDirEntry("hello.vbp", is_file=False)
        assert not is_file_of_extension(entry, ".vbp")
        assert not is_file_of_extension(entry, ".sln")
        assert not is_file_of_extension(entry)

    def test_file(self):
        entry = MockDirEntry("hello.vbp")
        assert is_file_of_extension(entry)
        assert is_file_of_extension(entry, ".vbp")
        assert not is_file_of_extension(entry, ".sln")
        assert is_file_of_extension(entry, ".vbg", ".vbp")
        assert not is_file_of_extension(entry, ".sln", ".xml")
        assert not is_file_of_extension(entry, ".bp")


class MockDirEntry:
    """Mock directory entry"""

    def __init__(self, name, is_file=True):
        """Creates an instance of this class"""
        self.name = name
        self._is_file = is_file

    def is_file(self):
        """Returns True if the entry is a file"""
        return self._is_file
