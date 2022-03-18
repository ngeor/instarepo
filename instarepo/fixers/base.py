import os
import os.path
from typing import List
import instarepo.fixers.context
import instarepo.git


class CompositeFix:
    def __init__(self, rules):
        self.rules = rules

    def run(self):
        result: List[str] = []
        for rule in self.rules:
            result.extend(rule.run())
        return result


class SingleFileFix:
    def __init__(self, git: instarepo.git.GitWorkingDir, filename: str, msg: str):
        self.git = git
        self.filename = filename
        self.msg = msg

    def run(self):
        filename = os.path.join(self.git.dir, self.filename)
        if not os.path.isfile(filename):
            return []
        with open(filename, "r", encoding="utf-8") as file:
            contents = file.read()
        converted_contents = self.convert(contents)
        if contents == converted_contents:
            return []
        with open(filename, "w", encoding="utf-8") as file:
            file.write(converted_contents)
        self.git.add(self.filename)
        self.git.commit(self.msg)
        return [self.msg]

    def convert(self, contents: str) -> str:
        return contents


class MissingFileFix:
    def __init__(
        self,
        context: instarepo.fixers.context.Context,
    ):
        self.context = context

    def run(self):
        filename = self.get_filename()
        if not filename:
            raise ValueError("filename cannot be empty")
        parts = filename.replace("\\", "/").split("/")
        for part in parts:
            if not part:
                raise ValueError(f"Found empty path segment in {filename}")
        directory_parts = parts[0:-1]
        filename_part = parts[-1]
        ensure_directories(self.context.git, *directory_parts)
        relative_filename = os.path.join(*directory_parts, filename_part)
        full_filename = self.context.git.join(relative_filename)
        file_already_exists = os.path.isfile(full_filename)
        if file_already_exists and not self.should_overwrite():
            return []
        if not self.should_process_repo():
            return []
        contents = self.get_contents()
        if not contents:
            return []
        if file_already_exists:
            with open(full_filename, "r", encoding="utf-8") as file:
                if contents == file.read():
                    return []
        with open(full_filename, "w", encoding="utf8") as file:
            file.write(contents)
        self.context.git.add(relative_filename)
        msg = "chore: {0} {1}".format(
            "Updated" if file_already_exists else "Adding", relative_filename
        )
        self.context.git.commit(msg)
        return [msg]

    def get_contents(self) -> str:
        return ""

    def get_filename(self) -> str:
        raise ValueError(
            "Please override this method and provide the relative path of the filename"
        )

    def should_process_repo(self) -> bool:
        return True

    def should_overwrite(self) -> bool:
        return False


def ensure_directories(git: instarepo.git.GitWorkingDir, *args):
    """
    Ensures that the given directories exist in the Git working directory.
    You can provide directories one by one, or separated by slash.
    """
    root = git.dir
    for directory in args:
        parts = directory.replace("\\", "/").split("/")
        for part in parts:
            root = os.path.join(root, part)
            if not os.path.isdir(root):
                os.mkdir(root)
