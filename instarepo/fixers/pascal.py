import functools
import logging
import os
import os.path
import subprocess

import instarepo.git
from instarepo.fixers.base import MissingFileFix

JCF_EXE = "C:\\opt\\jcf_243_exe\\JCF.exe"


def trim_trailing_whitespace(filename: str):
    with open(filename, "r", encoding="utf-8") as f:
        lines = f.readlines()
    lines = [line.rstrip() + "\n" for line in lines]
    with open(filename, "w", encoding="utf-8") as f:
        f.writelines(lines)


@functools.lru_cache(maxsize=None)
def find_jedi_cfg():
    local_app_data_dir = os.getenv("LOCALAPPDATA")
    if not local_app_data_dir:
        return ""
    if not os.path.isdir(local_app_data_dir):
        return ""
    lazarus_dir = os.path.join(local_app_data_dir, "lazarus")
    if not os.path.isdir(lazarus_dir):
        return ""
    cfg_file = os.path.join(lazarus_dir, "jcfsettings.cfg")
    if not os.path.isfile(cfg_file):
        return ""
    return cfg_file


def is_pascal_entry(entry):
    return entry.is_file() and (
        entry.name.endswith(".pas") or entry.name.endswith(".lpr")
    )


def is_lazarus_project(directory: str) -> bool:
    """
    Checks if the given directory is a Lazarus project.
    """
    with os.scandir(directory) as it:
        for entry in it:
            if entry.name.endswith(".lpr") and entry.is_file():
                return True
    return False


class AutoFormat:
    """Automatically formats Pascal files with JEDI code format"""
    def __init__(self, git: instarepo.git.GitWorkingDir):
        self.git = git
        self.files = []
        self._fallback_ptop_cfg = None

    def run(self):
        if not os.path.isfile(JCF_EXE):
            logging.debug("JEDI Code Format exe %s not found", JCF_EXE)
            return []
        if not find_jedi_cfg():
            logging.debug("JEDI Code Format cfg not found")
            return []
        with os.scandir(self.git.dir) as it:
            for entry in it:
                if is_pascal_entry(entry):
                    self._process(entry.path)
        if len(self.files) <= 0:
            return []
        msg = "Auto-formatted Pascal files: " + ", ".join(self.files)
        self.git.commit(msg)
        return [msg]

    def _process(self, pas_file: str):
        with open(pas_file, "r", encoding="utf-8") as f:
            old_contents = f.read()
        rel_path = os.path.relpath(pas_file, self.git.dir)
        # pass through jcf
        subprocess.run(self._build_args(rel_path), check=True, cwd=self.git.dir)
        # trim trailing whitespace
        trim_trailing_whitespace(pas_file)
        # check if we have changes
        with open(pas_file, "r", encoding="utf-8") as f:
            new_contents = f.read()
        if old_contents != new_contents:
            self.git.add(rel_path)
            self.files.append(rel_path)

    def _build_args(self, rel_pas_file: str) -> list[str]:
        args = [
            JCF_EXE,
            "-config=" + find_jedi_cfg(),
            "-clarify",
            "-inplace",
            "-y",
            "-f",
            rel_pas_file,
        ]
        return args


LAZARUS_GITIGNORE = """*.o
*.ppu
*.obj
*.exe
*.dll
*.compiled
*.bak
*.lps
backup/
"""


class MustHaveLazarusGitIgnore(MissingFileFix):
    """If missing, adds a gitignore file for Lazarus projects"""
    def __init__(self, git: instarepo.git.GitWorkingDir):
        super().__init__(git, ".gitignore")

    def should_process_repo(self):
        return is_lazarus_project(self.git.dir)

    def get_contents(self):
        return LAZARUS_GITIGNORE
