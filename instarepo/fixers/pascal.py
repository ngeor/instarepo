import functools
import logging
import os
import os.path
import subprocess
import instarepo.fixers.context
import instarepo.git

JCF_EXE = "C:\\opt\\jcf_243_exe\\JCF.exe"


def trim_trailing_whitespace(filename: str):
    with open(filename, "r", encoding="utf-8") as file:
        lines = file.readlines()
    lines = [line.rstrip() + "\n" for line in lines]
    with open(filename, "w", encoding="utf-8") as file:
        file.writelines(lines)


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


class AutoFormatFix:
    """Automatically formats Pascal files with JEDI code format"""

    def __init__(self, context: instarepo.fixers.context.Context):
        self.git = context.git
        self.files = []
        self._fallback_ptop_cfg = None
        self.verbose = context.verbose

    def run(self):
        if not os.path.isfile(JCF_EXE):
            logging.debug("JEDI Code Format exe %s not found", JCF_EXE)
            return []
        if not find_jedi_cfg():
            logging.debug("JEDI Code Format cfg not found")
            return []
        with os.scandir(self.git.dir) as iterator:
            for entry in iterator:
                if is_pascal_entry(entry):
                    self._process(entry.path)
        if len(self.files) <= 0:
            return []
        msg = "chore: Auto-formatted Pascal files: " + ", ".join(self.files)
        self.git.commit(msg)
        return [msg]

    def _process(self, pas_filename: str):
        with open(pas_filename, "r", encoding="utf-8") as file:
            old_contents = file.read()
        rel_path = os.path.relpath(pas_filename, self.git.dir)
        # pass through jcf
        if self.verbose:
            subprocess.run(self._build_args(rel_path), check=True, cwd=self.git.dir)
        else:
            subprocess.run(
                self._build_args(rel_path),
                check=True,
                cwd=self.git.dir,
                stdout=subprocess.PIPE,
            )
        # trim trailing whitespace
        trim_trailing_whitespace(pas_filename)
        # check if we have changes
        with open(pas_filename, "r", encoding="utf-8") as file:
            new_contents = file.read()
        if old_contents != new_contents:
            self.git.add(rel_path)
            self.files.append(rel_path)

    def _build_args(self, rel_pas_filename: str):
        args = [
            JCF_EXE,
            "-config=" + find_jedi_cfg(),
            "-clarify",
            "-inplace",
            "-y",
            "-f",
            rel_pas_filename,
        ]
        return args
