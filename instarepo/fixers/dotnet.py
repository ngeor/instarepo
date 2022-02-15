"""Fixers for .NET projects"""
import logging
import os
import os.path
import xml.etree.ElementTree as ET
from typing import Iterable, List, Optional

import instarepo.git
import instarepo.github
import instarepo.xml_utils
from .base import ensure_directories
from .finders import is_file_of_extension


class DotNetFrameworkVersionFix:
    """Sets the .NET Framework version to 4.7.2 in csproj and web.config files"""

    def __init__(self, git: instarepo.git.GitWorkingDir, **kwargs):
        self.git = git
        self.result = []

    def run(self):
        # ensure abspath so that dirpath in the loop is also absolute
        self.result = []
        with os.scandir(self.git.dir) as iterator:
            for entry in iterator:
                if is_file_of_extension(entry, ".sln"):
                    self.process_sln(entry.path)
        return self.result

    def process_sln(self, sln_path: str):
        for relative_csproj in get_projects_from_sln_file(sln_path):
            parts = relative_csproj.replace("\\", "/").split("/")
            abs_csproj = os.path.join(self.git.dir, *parts)
            self.process_csproj(abs_csproj)
            directory_parts = parts[0:-1]
            csproj_dir = os.path.join(self.git.dir, *directory_parts)
            self.process_web_configs(csproj_dir)

    def process_web_configs(self, csproj_dir: str):
        for web_config in get_web_configs_from_dir(csproj_dir):
            self.process_web_config(web_config)

    def process_csproj(self, filename: str):
        logging.debug("Processing csproj %s", filename)
        ET.register_namespace("", "http://schemas.microsoft.com/developer/msbuild/2003")
        try:
            tree = instarepo.xml_utils.parse(filename)
            target_framework_version = instarepo.xml_utils.find_at_tree(
                tree,
                "{http://schemas.microsoft.com/developer/msbuild/2003}PropertyGroup",
                "{http://schemas.microsoft.com/developer/msbuild/2003}TargetFrameworkVersion",
            )
            if target_framework_version is None:
                return
            desired_framework_version = "v4.7.2"
            if target_framework_version.text == desired_framework_version:
                return
            target_framework_version.text = desired_framework_version
            tree.write(
                filename,
                xml_declaration=True,
                encoding="utf-8",
            )
        finally:
            ET.register_namespace(
                "msbuild", "http://schemas.microsoft.com/developer/msbuild/2003"
            )
        relpath = os.path.relpath(filename, self.git.dir)
        self.git.add(relpath)
        msg = f"chore: Upgraded {relpath} to .NET {desired_framework_version}"
        self.git.commit(msg)
        self.result.append(msg)

    def process_web_config(self, filename: str):
        logging.debug("Processing web.config %s", filename)
        tree = instarepo.xml_utils.parse(filename)
        compilation = instarepo.xml_utils.find_at_tree(
            tree, "system.web", "compilation"
        )
        if compilation is None:
            return
        desired_framework_version = "4.7.2"
        if compilation.attrib.get("targetFramework", "") == desired_framework_version:
            return
        compilation.attrib["targetFramework"] = desired_framework_version
        tree.write(
            filename,
            xml_declaration=True,
            encoding="utf-8",
        )
        relpath = os.path.relpath(filename, self.git.dir)
        self.git.add(relpath)
        msg = f"chore: Upgraded {relpath} to .NET {desired_framework_version}"
        self.git.commit(msg)
        self.result.append(msg)


class MustHaveGitHubActionFix:
    """
    Creates a GitHub Action workflow for CSharp projects, deletes appveyor.yml if present.
    Does not work for locally checked out repositories.
    """

    def __init__(
        self,
        git: instarepo.git.GitWorkingDir,
        repo: Optional[instarepo.github.Repo],
        **kwargs,
    ):
        self.git = git
        self.repo = repo

    def run(self):
        if not self._should_process_repo():
            return []

        if not self.repo:
            return []

        expected_contents = get_workflow_contents(self.repo)
        dir_name = ".github/workflows"
        ensure_directories(self.git, dir_name)
        file_name = dir_name + "/build.yml"
        absolute_file_name = self.git.join(file_name)
        if os.path.isfile(absolute_file_name):
            with open(absolute_file_name, "r", encoding="utf-8") as file:
                old_contents = file.read()
        else:
            old_contents = ""
        if expected_contents != old_contents:
            with open(absolute_file_name, "w", encoding="utf-8") as file:
                file.write(expected_contents)
            self.git.add(file_name)
            if old_contents:
                msg = "chore: Updated GitHub Actions workflow for .NET project"
            else:
                msg = "chore: Added GitHub Actions workflow for .NET project"
            self._rm_appveyor()
            self.git.commit(msg)
            return [msg]
        if self._rm_appveyor():
            msg = "chore: Removed appveyor.yml from .NET project"
            self.git.commit(msg)
            return [msg]
        return []

    def _should_process_repo(self) -> bool:
        """
        Checks if the repo should be processed.
        The repo should be processed if it contains exactly one sln file
        at the root directory which references at least one csproj file.
        """
        sln_path = ""
        with os.scandir(self.git.dir) as iterator:
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
        if self.git.isfile("appveyor.yml"):
            self.git.rm("appveyor.yml")
            return True
        return False


def get_workflow_contents(repo: instarepo.github.Repo):
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
        "trunk", repo.default_branch
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
    for line in contents.splitlines():
        if line.startswith('Project("{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}")'):
            parts = line.split(",")
            csproj = parts[1].strip()
            if csproj.startswith('"'):
                csproj = csproj[1:].strip()
            if csproj.endswith('"'):
                csproj = csproj[:-1].strip()
            yield csproj


def get_web_configs_from_dir(csproj_dir: str) -> Iterable[str]:
    """
    Gets the files named web.config in a directory.
    In a case-sensitive file system, if the directory contains both
    web.config and Web.Config, both will be returned.
    The iterator yields absolute paths.
    """
    with os.scandir(csproj_dir) as iterator:
        for entry in iterator:
            if entry.is_file() and entry.name.lower() == "web.config":
                yield entry.path
