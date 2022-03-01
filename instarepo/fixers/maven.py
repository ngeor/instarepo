"""Fixes for Maven projects"""
import os
import os.path
import platform
import subprocess
import tempfile
import xml.etree.ElementTree as ET

import requests

import instarepo.fixers.context
import instarepo.git
import instarepo.github
import instarepo.xml_utils
from instarepo.fixers.base import MissingFileFix
from .finders import is_maven_project
from .readme import locate_badges, merge_badges


MAVEN_YML = """# This workflow will build a Java project with Maven, and cache/restore any dependencies to improve the workflow execution time
# For more information see: https://help.github.com/actions/language-and-framework-guides/building-and-testing-java-with-maven

name: Java CI with Maven

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
    - name: Set up JDK 11
      uses: actions/setup-java@v2
      with:
        java-version: '11'
        distribution: 'adopt'
        cache: maven
    - name: Build with Maven
      run: mvn -B package --file pom.xml
"""


class MustHaveCIFix(MissingFileFix):
    """If missing, adds a GitHub action Maven build workflow"""

    def __init__(self, context: instarepo.fixers.context.Context):
        super().__init__(context.git, ".github/workflows/maven.yml")
        self.context = context

    def should_process_repo(self):
        return is_maven_project(self.git.dir)

    def get_contents(self):
        return MAVEN_YML.replace("trunk", self.context.default_branch())


class MavenBadgesFix:
    """
    Fixes badges for Maven libraries.

    Does not work for local git repositories.
    """

    def __init__(self, context: instarepo.fixers.context.Context):
        self.context = context
        self.maven = Maven(context.git.dir)

    def run(self):
        if not self.context.git.isfile("README.md"):
            return []
        if not self.context.git.isfile("pom.xml"):
            return []
        if not self.context.repo:
            return []
        badges = self._badges_dict(self.context.repo)

        if not badges:
            return []

        with open(self.context.git.join("README.md"), "r", encoding="utf-8") as file:
            before_badges, existing_badges, after_badges = locate_badges(file.read())
            has_changes = False
            for i in range(len(existing_badges)):
                existing_badge = existing_badges[i]
                for needle, markdown in list(badges.items()):
                    if needle in existing_badge:
                        # delete the badge from the dictionary
                        # so that we don't add it again later
                        del badges[needle]
                        if existing_badge != markdown:
                            has_changes = True
                            existing_badges[i] = markdown
                        break
            if badges:
                existing_badges.extend(badges.values())
                has_changes = True
        if not has_changes:
            return []
        with open(self.context.git.join("README.md"), "w", encoding="utf-8") as file:
            file.write(merge_badges(before_badges, existing_badges, after_badges))
        self.context.git.add("README.md")
        msg = "Updated Maven badges in README.md"
        self.context.git.commit(msg)
        return [msg]

    def _badges_dict(self, repo: instarepo.github.Repo):
        badges = {}
        badges.update(self._github_actions_badge(repo))
        badges.update(self._effective_pom_badges())
        return badges

    def _github_actions_badge(self, repo: instarepo.github.Repo):
        if self.context.git.isfile(".github", "workflows", "maven.yml"):
            needle = "actions/workflows"
            markdown = f"[![Java CI with Maven](https://github.com/{repo.full_name}/actions/workflows/maven.yml/badge.svg)](https://github.com/{repo.full_name}/actions/workflows/maven.yml)"
            return {needle: markdown}
        return {}

    def _effective_pom_badges(self):
        badges = {}
        with tempfile.TemporaryDirectory() as tmp_dir:
            filename = os.path.join(tmp_dir, "pom.xml")
            self.maven.run("-B", "help:effective-pom", f"-Doutput={filename}")
            tree = instarepo.xml_utils.parse(filename)
            root = tree.getroot()
            badges.update(maven_central_badge(root))
            # edge case for checkstyle-rules artifact which has to publish
            # javadoc but doesn't have any source code
            if self.context.git.isdir("src", "main", "java"):
                badges.update(javadoc_badge(root))
        return badges


def maven_central_badge(root: ET.Element):
    group_id = root.findtext("{http://maven.apache.org/POM/4.0.0}groupId")
    if not group_id:
        return {}
    artifact_id = root.findtext("{http://maven.apache.org/POM/4.0.0}artifactId")
    if not artifact_id:
        return {}
    group_id_as_path = group_id.replace(".", "/")
    url = f"https://repo1.maven.org/maven2/{group_id_as_path}/{artifact_id}/"
    response = requests.get(url)
    if not response.ok:
        return {}
    needle = "maven-central"
    markdown = f"[![Maven Central](https://img.shields.io/maven-central/v/{group_id}/{artifact_id}.svg?label=Maven%20Central)](https://search.maven.org/search?q=g:%22{group_id}%22%20AND%20a:%22{artifact_id}%22)"
    return {needle: markdown}


def javadoc_badge(root: ET.Element):
    plugins = instarepo.xml_utils.find(
        root,
        "{http://maven.apache.org/POM/4.0.0}build",
        "{http://maven.apache.org/POM/4.0.0}plugins",
    )
    if plugins is None:
        return {}
    uses_maven_source_plugin = False
    uses_maven_javadoc_plugin = False
    for plugin in plugins:
        plugin_artifact_id = plugin.findtext(
            "{http://maven.apache.org/POM/4.0.0}artifactId"
        )
        if plugin_artifact_id == "maven-source-plugin":
            if "jar-no-fork" in plugin_goals(plugin):
                uses_maven_source_plugin = True
        if plugin_artifact_id == "maven-javadoc-plugin":
            if "jar" in plugin_goals(plugin):
                uses_maven_javadoc_plugin = True
    if not (uses_maven_source_plugin and uses_maven_javadoc_plugin):
        return {}
    group_id = root.findtext("{http://maven.apache.org/POM/4.0.0}groupId")
    if not group_id:
        return {}
    artifact_id = root.findtext("{http://maven.apache.org/POM/4.0.0}artifactId")
    if not artifact_id:
        return {}
    needle = "javadoc"
    markdown = f"[![javadoc](https://javadoc.io/badge2/{group_id}/{artifact_id}/javadoc.svg)](https://javadoc.io/doc/{group_id}/{artifact_id})"
    return {needle: markdown}


def plugin_goals(plugin: ET.Element):
    executions = plugin.find("{http://maven.apache.org/POM/4.0.0}executions")
    if executions is None:
        return set()
    executions = executions.findall("{http://maven.apache.org/POM/4.0.0}execution")
    goals = map(
        lambda x: x.find("{http://maven.apache.org/POM/4.0.0}goals"),
        executions,
    )
    goals = [x for x in goals if x]
    return set(
        y.text
        for x in goals
        for y in x.findall("{http://maven.apache.org/POM/4.0.0}goal")
        if y.text
    )


class Maven:
    """
    Runs Maven commands.
    """

    def __init__(self, directory: str):
        """
        Creates an instance of this class.

        :param directory: The directory of a Maven project
        """
        self.directory = directory

    # pylint: disable=subprocess-run-check
    def run(self, *args) -> str:
        """
        Runs Maven commands.
        """
        mvn_executable = "mvn.cmd" if platform.system() == "Windows" else "mvn"
        result = subprocess.run(
            [mvn_executable, *args],
            cwd=self.directory,
            encoding="utf-8",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        maven_output = result.stdout.strip()
        if result.returncode != 0:
            raise ChildProcessError(maven_output)
        return maven_output

    def sort_pom(self):
        self.run(
            "-B",
            "com.github.ekryd.sortpom:sortpom-maven-plugin:sort",
            "-Dsort.createBackupFile=false",
        )


class UrlFix:
    """
    Ensures Maven projects have the correct URL and SCM sections.

    Does not work for local git repositories.
    """

    def __init__(self, context: instarepo.fixers.context.Context):
        self.context = context

    def run(self):
        if not self.context.git.isfile("pom.xml") or not self.context.repo:
            return []
        try:
            ET.register_namespace("", "http://maven.apache.org/POM/4.0.0")
            return self.do_run(self.context.repo)
        finally:
            ET.register_namespace("maven", "http://maven.apache.org/POM/4.0.0")

    def do_run(self, repo: instarepo.github.Repo):
        has_changes = False
        tree = instarepo.xml_utils.parse(self.context.git.join("pom.xml"))
        root = tree.getroot()
        has_changes |= ensure_element(
            root, "{http://maven.apache.org/POM/4.0.0}url", repo.html_url
        )
        scm = root.find("{http://maven.apache.org/POM/4.0.0}scm")
        if scm is None:
            has_changes = True
            scm = ET.Element("{http://maven.apache.org/POM/4.0.0}scm")
            root.append(scm)
        has_changes |= ensure_element(
            scm,
            "{http://maven.apache.org/POM/4.0.0}connection",
            f"scm:git:{repo.clone_url}",
        )
        has_changes |= ensure_element(
            scm,
            "{http://maven.apache.org/POM/4.0.0}developerConnection",
            f"scm:git:{repo.ssh_url}",
        )
        has_changes |= ensure_element(
            scm, "{http://maven.apache.org/POM/4.0.0}tag", "HEAD"
        )
        has_changes |= ensure_element(
            scm, "{http://maven.apache.org/POM/4.0.0}url", repo.html_url
        )
        if has_changes:
            tree.write(self.context.git.join("pom.xml"))
            Maven(self.context.git.dir).sort_pom()
            self.context.git.add("pom.xml")
            msg = "Corrected url info in pom.xml"
            self.context.git.commit(msg)
            return [msg]

        return []


def ensure_element(parent: ET.Element, child_name: str, child_text: str) -> bool:
    has_changes = False
    child_element = parent.find(child_name)
    if child_element is None:
        has_changes = True
        child_element = ET.Element(child_name)
        parent.append(child_element)
    if child_element.text != child_text:
        has_changes = True
        child_element.text = child_text
    return has_changes
