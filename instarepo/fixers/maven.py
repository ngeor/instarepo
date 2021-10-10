import os.path
import platform
import re
import subprocess

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

    def run(self):
        full_filename = os.path.join(self.git.dir, "pom.xml")
        if not os.path.isfile(full_filename):
            return []

        commits = []

        old_modified_time = os.path.getmtime(full_filename)
        update_properties_output = self.update_properties()
        update_properties_had_changes = old_modified_time != os.path.getmtime(
            full_filename
        )
        if update_properties_had_changes:
            self.git.add("pom.xml")
            msg = "Updated Maven dependencies\n\n" + update_properties_output + "\n"
            self.git.commit(msg)
            commits.append(msg)

        old_modified_time = os.path.getmtime(full_filename)
        update_parent_output = self.update_parent()
        update_parent_had_changes = old_modified_time != os.path.getmtime(full_filename)
        if update_parent_had_changes:
            self.git.add("pom.xml")
            msg = "Updated parent pom\n\n" + update_parent_output + "\n"
            self.git.commit(msg)
            commits.append(msg)

        return commits

    # TODO also update non properties
    # TODO fix broken parent pom

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
    ]
    for deny_prefix in deny_prefixes:
        if line.startswith(deny_prefix):
            return False
    return True
