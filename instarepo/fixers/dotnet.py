"""Fixers for .NET projects"""
import os
import os.path
from typing import Iterable, List

import instarepo.fixers.context
import instarepo.git
import instarepo.github
import instarepo.xml_utils
from .base import ensure_directories
from .finders import is_file_of_extension
from ..parsers import (
    many,
    combine_or,
    word,
    one_char_if,
    quoted_string,
    combine_and_opt,
    surrounded_by_space,
    is_symbol,
    until_eol_or_eof,
    is_cr_lf,
    any_char,
)


class MustHaveGitHubActionFix:
    """
    Creates a GitHub Action workflow for CSharp projects, deletes appveyor.yml if present.
    """

    def __init__(self, context: instarepo.fixers.context.Context):
        self.context = context

    def run(self):
        if not self._should_process_repo():
            return []

        expected_contents = get_workflow_contents(self.context.default_branch())
        dir_name = ".github/workflows"
        ensure_directories(self.context.git, dir_name)
        file_name = dir_name + "/build.yml"
        absolute_file_name = self.context.git.join(file_name)
        if os.path.isfile(absolute_file_name):
            with open(absolute_file_name, "r", encoding="utf-8") as file:
                old_contents = file.read()
        else:
            old_contents = ""
        if expected_contents != old_contents:
            with open(absolute_file_name, "w", encoding="utf-8") as file:
                file.write(expected_contents)
            self.context.git.add(file_name)
            if old_contents:
                msg = "chore: Updated GitHub Actions workflow for .NET project"
            else:
                msg = "chore: Added GitHub Actions workflow for .NET project"
            self._rm_appveyor()
            self.context.git.commit(msg)
            return [msg]
        if self._rm_appveyor():
            msg = "chore: Removed appveyor.yml from .NET project"
            self.context.git.commit(msg)
            return [msg]
        return []

    def _should_process_repo(self) -> bool:
        """
        Checks if the repo should be processed.
        The repo should be processed if it contains exactly one sln file
        at the root directory which references at least one csproj file.
        """
        sln_path = ""
        with os.scandir(self.context.git.dir) as iterator:
            for entry in iterator:
                if is_file_of_extension(entry, ".sln"):
                    if sln_path:
                        # multiple sln files not supported currently
                        return False
                    else:
                        sln_path = entry.path
        if not sln_path:
            return False
        return len(get_projects_from_sln_file(sln_path)) > 0

    def _rm_appveyor(self):
        if self.context.git.isfile("appveyor.yml"):
            self.context.git.rm("appveyor.yml")
            return True
        return False


def get_workflow_contents(default_branch: str):
    return """name: CI

on:
  push:
    branches: [ trunk ]
  pull_request:
    branches: [ trunk ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up .NET
      uses: actions/setup-dotnet@v1
      with:
        dotnet-version: '3.1.x'
    - run: dotnet build
    - run: dotnet test -v normal
""".replace(
        "trunk", default_branch
    )


def get_projects_from_sln_file(path: str) -> List[str]:
    """
    Gets the projects defined in a sln file.

    :param path: The path of a Visual Studio sln file.
    """
    with open(path, "r", encoding="utf-8") as file:
        return list(get_projects_from_sln_file_contents(file.read()))


def get_projects_from_sln_file_contents(contents: str) -> Iterable[str]:
    """
    Gets the projects defined in a sln file.

    :param contents: The contents of a Visual Studio sln file.
    """
    return SlnProjectFinder(contents)


class SlnProjectFinder:
    def __init__(self, contents: str):
        self._parser = SlnParser(contents)

    def next(self):
        while self._parser.find("Project"):
            project_path = self._read_project_path()
            if project_path:
                return project_path

    def _read_project_path(self):
        lparen = self._parser.next()
        if lparen != "(":
            return
        project_type_guid = self._parser.next()
        if project_type_guid[1:-1] not in [
            "{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}",
            "{9A19103F-16F7-4668-BE54-9A1E7A4F7556}",
        ]:
            return
        rparen = self._parser.next()
        if rparen != ")":
            return
        eq = self._parser.next()
        if eq != "=":
            return
        _project_name = self._parser.next()
        comma = self._parser.next()
        if comma != ",":
            return
        csproj_path = self._parser.next()
        return csproj_path[1:-1]

    def __iter__(self):
        return self

    def __next__(self):
        result = self.next()
        if result:
            return result
        else:
            raise StopIteration


class SlnParser:
    def __init__(self, contents: str):
        self._contents = contents
        self._parser = combine_or(
            comment(),
            word(),
            version_number(),
            quoted_string(),
            surrounded_by_space(one_char_if(is_symbol)),
            many(one_char_if(is_cr_lf)),
            any_char(),
        )

    def next(self):
        result, remaining = self._parser(self._contents)
        self._contents = remaining
        return result

    def find(self, needle: str):
        """
        Returns the first token that is equal to the parameter.
        """
        token = self.next()
        while token and token != needle:
            token = self.next()
        return token


def version_number():
    return many(one_char_if(lambda char: char == "." or (char >= "0" and char <= "9")))


def comment():
    return combine_and_opt(one_char_if(lambda ch: ch == "#"), until_eol_or_eof())
