"""Fixers for .NET projects"""
import logging
import os
import os.path
from string import Template
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


class MustHaveCIFix:
    """
    Creates a GitHub Action workflow for CSharp projects, deletes appveyor.yml if present.
    """

    def __init__(self, context: instarepo.fixers.context.Context):
        self.context = context

    def run(self):
        sln_paths = list(self._get_sln_paths())
        # multiple sln files not supported
        if len(sln_paths) != 1:
            return []
        sln_path = sln_paths[0]
        cs_projects = [
            self.context.git.join(relative_cs_proj)
            for relative_cs_proj in get_projects_from_sln_file(sln_path)
        ]
        if not cs_projects:
            return []
        rel_sln_path = os.path.relpath(sln_path, self.context.git.dir)
        sln_name, _ = os.path.splitext(os.path.basename(sln_path))
        needs_windows = any(
            filter(lambda x: x == "windows", map(csproj_file_to_os, cs_projects))
        )
        if needs_windows:
            artifact_path = f"{sln_name}*/bin/Release/{sln_name}*.*"
            expected_contents = get_windows_workflow_contents(
                self.context.default_branch(), rel_sln_path, artifact_path
            )
        else:
            artifact_path = f"{sln_name}*/bin/Release/*/{sln_name}*.*"
            expected_contents = get_linux_workflow_contents(
                self.context.default_branch(), artifact_path
            )
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

    def _get_sln_paths(self):
        with os.scandir(self.context.git.dir) as iterator:
            for entry in iterator:
                if is_file_of_extension(entry, ".sln"):
                    yield entry.path

    def _rm_appveyor(self):
        if self.context.git.isfile("appveyor.yml"):
            self.context.git.rm("appveyor.yml")
            return True
        return False


def get_linux_workflow_contents(default_branch: str, artifact_path: str):
    template = Template(
        """name: CI

on:
  push:
    branches: [ ${default_branch} ]
  pull_request:
    branches: [ ${default_branch} ]

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
    - run: dotnet build -c Release
    - name: Upload binaries
      uses: actions/upload-artifact@v3
      with:
        name: binaries
        path: ${artifact_path}
"""
    )
    return template.substitute(
        default_branch=default_branch, artifact_path=artifact_path
    )


def get_windows_workflow_contents(
    default_branch: str, sln_path: str, artifact_path: str
):
    template = Template(
        """name: CI

on:
  push:
    branches: [ ${default_branch} ]
  pull_request:
    branches: [ ${default_branch} ]

jobs:
  build:
    runs-on: windows-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v2
    - name: Add msbuild to PATH # https://github.com/microsoft/setup-msbuild
      uses: microsoft/setup-msbuild@v1.1
    - name: Setup NuGet # https://github.com/NuGet/setup-nuget
      uses: nuget/setup-nuget@v1
    - name: Restore NuGet packages
      run: nuget restore ${sln_path}
    - name: Build project
      run: msbuild -t:rebuild -property:Configuration=Release ${sln_path}
    - name: Upload binaries
      uses: actions/upload-artifact@v3
      with:
        name: binaries
        path: ${artifact_path}
"""
    )
    return template.substitute(
        default_branch=default_branch, sln_path=sln_path, artifact_path=artifact_path
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


def csproj_file_to_os(csproj_filename):
    tree = instarepo.xml_utils.parse(csproj_filename)
    if tree is None:
        logging.warning("Could not parse %s", csproj_filename)
        return
    return csproj_root_node_to_os(tree.getroot(), csproj_filename)


def csproj_root_node_to_os(root_node, csproj_filename=""):
    """
    Determines the OS needed by the given csproj file. The root_node
    is the root node of the parsed XML file.
    """
    if root_node is None:
        logging.warning("No root node for csproj file %s", csproj_filename)
        return
    if root_node.tag == "{http://schemas.microsoft.com/developer/msbuild/2003}Project":
        return "windows"
    node = instarepo.xml_utils.find(root_node, "PropertyGroup", "TargetFramework")
    if node is None:
        logging.warning("Could not find target framework of %s", csproj_filename)
        return
    if not node.text:
        logging.warning("Empty TargetFramework for %s", csproj_filename)
        return
    if node.text.startswith("net4"):
        return "windows"
    if node.text.startswith("netcore") or node.text.startswith("netstandard"):
        return "linux"
