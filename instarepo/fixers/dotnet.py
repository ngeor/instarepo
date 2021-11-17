"""Fixers for .NET projects"""
import logging
import os
import os.path
import xml.etree.ElementTree as ET
from typing import Iterable

import instarepo.git
import instarepo.xml_utils
from instarepo.fixers.base import MissingFileFix
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
        msg = f"Upgraded {relpath} to .NET {desired_framework_version}"
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
        msg = f"Upgraded {relpath} to .NET {desired_framework_version}"
        self.git.commit(msg)
        self.result.append(msg)


class MustHaveCSharpAppVeyor(MissingFileFix):
    """If missing, creates an appveyor.yml file for CSharp projects"""

    def __init__(self, git: instarepo.git.GitWorkingDir, **kwargs):
        super().__init__(git, "appveyor.yml")

    def should_process_repo(self) -> bool:
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

    def get_contents(self):
        return """version: 1.0.{build}
assembly_info:
  patch: true
  file: '**\\AssemblyInfo.*'
  assembly_version: '{version}'
  assembly_file_version: '{version}'
  assembly_informational_version: '{version}'
before_build:
- nuget restore
build:
  verbosity: minimal
"""


def get_projects_from_sln_file(path: str) -> list[str]:
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
