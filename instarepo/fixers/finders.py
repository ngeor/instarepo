"""
Functions that determine the project's language or build system.
"""

import os
import os.path


def is_lazarus_project(directory: str) -> bool:
    """
    Checks if the given directory is a Lazarus project.
    """
    return has_file_of_extension(directory, ".lpr")


def is_maven_project(directory: str) -> bool:
    """
    Checks if the given directory is a Maven project.
    """
    return os.path.isfile(os.path.join(directory, "pom.xml"))


def is_vb6_project(directory: str) -> bool:
    """
    Checks if the given directory is a VB6 project.
    """
    return has_file_of_extension(directory, ".vbp", ".vbg")


def has_file_of_extension(directory: str, *args) -> bool:
    """
    Checks if the given directory has a file of the
    given file extensions.

    Extensions are passed in the args parameter and
    must be prefixed by a dot.
    """
    with os.scandir(directory) as iterator:
        for entry in iterator:
            if is_file_of_extension(entry, *args):
                return True
    return False


def is_file_of_extension(entry, *args):
    """
    Checks if the given directory entry is a file
    and ends in one of the given extensions.

    Extensions are passed in the args parameter and
    must be prefixed by a dot.
    """
    if not entry.is_file():
        return False
    if not args:
        return True
    for arg in args:
        if entry.name.endswith(arg):
            return True
    return False
