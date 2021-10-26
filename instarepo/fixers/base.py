import os.path

import instarepo.git


class CompositeFix:
    def __init__(self, rules):
        self.rules = rules

    def run(self):
        result = []
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
        with open(filename, "r") as f:
            contents = f.read()
        converted_contents = self.convert(contents)
        if contents == converted_contents:
            return []
        with open(filename, "w") as f:
            f.write(converted_contents)
        self.git.add(self.filename)
        self.git.commit(self.msg)
        return [self.msg]

    def convert(self, contents: str) -> str:
        return contents


class MissingFileFix:
    def __init__(
        self,
        git: instarepo.git.GitWorkingDir,
        filename: str,
    ):
        self.git = git
        if not filename:
            raise ValueError("filename cannot be empty")
        parts = filename.replace("\\", "/").split("/")
        for part in parts:
            if not part:
                raise ValueError(f"Found empty path segment in {filename}")
        self.directory_parts = parts[0:-1]
        self.filename_part = parts[-1]

    def run(self):
        self._ensure_directories()
        relative_filename = os.path.join(*self.directory_parts, self.filename_part)
        full_filename = os.path.join(self.git.dir, relative_filename)
        if os.path.isfile(full_filename):
            return []
        if not self.should_process_repo():
            return []
        contents = self.get_contents()
        if contents is None:
            return []
        with open(full_filename, "w", encoding="utf8") as f:
            f.write(contents)
        self.git.add(relative_filename)
        msg = "Adding " + relative_filename
        self.git.commit(msg)
        return [msg]

    def get_contents(self) -> str:
        return None

    def should_process_repo(self) -> bool:
        return True

    def _ensure_directories(self):
        root = self.git.dir
        for dir in self.directory_parts:
            root = os.path.join(root, dir)
            if not os.path.isdir(root):
                os.mkdir(root)
