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


class ReadmeFix:
    def __init__(self, git: instarepo.git.GitWorkingDir):
        self.git = git

    def run(self):
        filename = os.path.join(self.git.dir, "README.md")
        if not os.path.isfile(filename):
            return []
        with open(filename, "r") as f:
            s = f.read()
        return []


class DummyFix:
    def __init__(self, git: instarepo.git.GitWorkingDir):
        self.git = git

    def run(self):
        with open(os.path.join(self.git.dir, "test.txt"), "w") as f:
            f.write("hello, world")
        self.git.add("test.txt")
        self.git.commit("Adding a test.txt file")
        return ["Adding a test.txt file"]
