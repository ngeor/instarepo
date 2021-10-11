import os.path
import platform
import re
import subprocess
import xml.etree.ElementTree as ET

import requests

import instarepo.git
import instarepo.github


class MavenFix:
    def __init__(
        self,
        git: instarepo.git.GitWorkingDir,
        repo: instarepo.github.Repo,
    ):
        self.git = git
        self.repo = repo
        self._commits: list[str] = []
        self._full_filename: str = None

    def run(self):
        self._full_filename = os.path.join(self.git.dir, "pom.xml")
        if not os.path.isfile(self._full_filename):
            return []

        self._commits = []
        self.remove_snapshot_parent_pom()
        self.run_step("Using latest releases", self.use_latest_releases)
        self.run_step("Updated pom properties", self.update_properties)
        self.run_step("Updated parent pom", self.update_parent)
        return self._commits

    def remove_snapshot_parent_pom(self):
        parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
        tree = ET.parse(self._full_filename, parser=parser)
        if tree is None:
            return
        root = tree.getroot()
        if root is None:
            return
        parent = root.find("{http://maven.apache.org/POM/4.0.0}parent")
        if parent is None:
            return
        group_id = parent.find("{http://maven.apache.org/POM/4.0.0}groupId")
        if group_id is None:
            return
        artifact_id = parent.find("{http://maven.apache.org/POM/4.0.0}artifactId")
        if artifact_id is None:
            return
        version = parent.find("{http://maven.apache.org/POM/4.0.0}version")
        if version is None:
            return
        relative_path = parent.find("{http://maven.apache.org/POM/4.0.0}relativePath")
        has_changes = False
        if relative_path is not None and relative_path.text.startswith("../"):
            parent.remove(relative_path)
            has_changes = True
        if "SNAPSHOT" in version.text:
            version.text = get_latest_artifact_version(group_id.text, artifact_id.text)
            has_changes = True
        if has_changes:
            tree.write(
                self._full_filename,
                default_namespace="http://maven.apache.org/POM/4.0.0",
            )
            self.sort_pom()
            self.git.add("pom.xml")
            msg = "Corrected parent pom reference"
            self.git.commit(msg)
            self._commits.append(msg)

    def run_step(self, title: str, step_function):
        old_modified_time = os.path.getmtime(self._full_filename)
        output = step_function()
        had_changes = old_modified_time != os.path.getmtime(self._full_filename)
        if had_changes:
            self.sort_pom()
            self.git.add("pom.xml")
            msg = title + "\n\n" + output + "\n"
            self.git.commit(msg)
            self._commits.append(msg)

    def use_latest_releases(self):
        rules = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "maven_version_rules.xml"
        )
        # hack for running on Windows
        rules = "/" + rules.replace("\\", "/")
        mvn_executable = "mvn.cmd" if platform.system() == "Windows" else "mvn"
        result = subprocess.run(
            [
                mvn_executable,
                "-B",
                "versions:use-latest-releases",
                f"-Dmaven.version.rules=file://{rules}",
                "-DallowMajorUpdates=false"
            ],
            cwd=self.git.dir,
            encoding="utf-8",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        maven_output = result.stdout.strip()
        if result.returncode != 0:
            raise ChildProcessError(maven_output)
        return filter_maven_output(maven_output)

    def update_properties(self):
        rules = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "maven_version_rules.xml"
        )
        # hack for running on Windows
        rules = "/" + rules.replace("\\", "/")
        mvn_executable = "mvn.cmd" if platform.system() == "Windows" else "mvn"
        result = subprocess.run(
            [
                mvn_executable,
                "-B",
                "versions:update-properties",
                f"-Dmaven.version.rules=file://{rules}",
                "-DallowMajorUpdates=false"
            ],
            cwd=self.git.dir,
            encoding="utf-8",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        maven_output = result.stdout.strip()
        if result.returncode != 0:
            raise ChildProcessError(maven_output)
        return filter_maven_output(maven_output)

    def update_parent(self):
        mvn_executable = "mvn.cmd" if platform.system() == "Windows" else "mvn"
        result = subprocess.run(
            [
                mvn_executable,
                "-B",
                "versions:update-parent",
            ],
            cwd=self.git.dir,
            encoding="utf-8",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        maven_output = result.stdout.strip()
        if result.returncode != 0:
            raise ChildProcessError(maven_output)
        return filter_maven_output(maven_output)

    def sort_pom(self):
        mvn_executable = "mvn.cmd" if platform.system() == "Windows" else "mvn"
        subprocess.run(
            [
                mvn_executable,
                "-B",
                "com.github.ekryd.sortpom:sortpom-maven-plugin:sort",
                "-Dsort.createBackupFile=false",
            ],
            cwd=self.git.dir,
            encoding="utf-8",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )


LOG_LEVEL = re.compile(r"^\[[A-Z]+\]")


def filter_maven_output(output: str) -> str:
    lines = output.splitlines()
    modified_lines = (map_line(line) for line in lines)
    filtered_lines = (line for line in modified_lines if filter_line(line))
    return os.linesep.join(filtered_lines)


def map_line(line: str) -> str:
    line = LOG_LEVEL.sub("", line)
    line = line.strip()
    return line


def filter_line(line: str) -> bool:
    if not line:
        return False
    deny_prefixes = [
        "Scanning",
        "-",
        "Building",
        "artifact",
        "Downloading",
        "Downloaded",
        "BUILD",
        "Total",
        "Finished",
        "Minor version",
        "Reactor "
    ]
    for deny_prefix in deny_prefixes:
        if line.startswith(deny_prefix):
            return False
    return True


def get_latest_artifact_version(group_id: str, artifact_id: str) -> str:
    group_path = group_id.replace(".", "/")
    url = (
        f"https://repo1.maven.org/maven2/{group_path}/{artifact_id}/maven-metadata.xml"
    )
    response = requests.get(url)
    response.raise_for_status()
    root = ET.fromstring(response.text)
    versioning = root.find("versioning")
    release = versioning.find("release")
    return release.text
