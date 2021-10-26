import logging
import os
import os.path
import xml.etree.ElementTree as ET

import instarepo.git
from instarepo.fixers.base import MissingFileFix


def is_csharp_project(dir: str) -> bool:
    """
    Checks if the given directory is a C# project.
    The directory must have a .sln file which references at least one C# project.
    """
    with os.scandir(dir) as it:
        for entry in it:
            if entry.name.endswith(".sln") and entry.is_file():
                return is_csharp_solution(entry.path)
    return False


def is_csharp_solution(sln_file: str) -> bool:
    """
    Checks if the given sln file references C# projects.
    """
    with open(sln_file, "r") as f:
        lines = f.readlines()
        # e.g. Project("{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}") = "CVRender", "CVRender\CVRender.csproj", "{BD17C766-DF9E-4117-A8CB-2BAA8FE6D9B9}"
        project_lines = [line for line in lines if line.startswith("Project(")]
        cs_proj_lines = [line for line in project_lines if ".csproj" in line]
        return len(cs_proj_lines) > 0


class DotNetFrameworkVersionFix:
    def __init__(
        self,
        git: instarepo.git.GitWorkingDir,
    ):
        self.git = git
        self.result = []

    def run(self):
        # ensure abspath so that dirpath in the loop is also absolute
        self.result = []
        for entry in os.walk(os.path.abspath(self.git.dir)):
            dirpath, dirnames, filenames = entry
            for filename in filenames:
                if filename.endswith(".csproj"):
                    self.process_csproj(os.path.join(dirpath, filename))
                elif filename.lower() == "web.config":
                    self.process_web_config(os.path.join(dirpath, filename))
        return self.result

    def process_csproj(self, filename: str):
        logging.debug("Processing csproj %s", filename)
        ET.register_namespace("", "http://schemas.microsoft.com/developer/msbuild/2003")
        try:
            parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
            tree = ET.parse(filename, parser=parser)
            if tree is None:
                return
            root = tree.getroot()
            if root is None:
                return
            property_group = root.find(
                "{http://schemas.microsoft.com/developer/msbuild/2003}PropertyGroup"
            )
            if property_group is None:
                return
            target_framework_version = property_group.find(
                "{http://schemas.microsoft.com/developer/msbuild/2003}TargetFrameworkVersion"
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
        parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
        tree = ET.parse(filename, parser=parser)
        if tree is None:
            return
        root = tree.getroot()
        if root is None:
            return
        system_web = root.find("system.web")
        if system_web is None:
            return
        compilation = system_web.find("compilation")
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
    def __init__(self, git: instarepo.git.GitWorkingDir):
        super().__init__(git, "appveyor.yml")

    def should_process_repo(self):
        return is_csharp_project(self.git.dir)

    def get_contents(self):
        return """version: 1.0.{build}
assembly_info:
  patch: true
  file: '**\AssemblyInfo.*'
  assembly_version: '{version}'
  assembly_file_version: '{version}'
  assembly_informational_version: '{version}'
before_build:
- nuget restore
build:
  verbosity: minimal
"""
