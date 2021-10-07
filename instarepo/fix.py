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
