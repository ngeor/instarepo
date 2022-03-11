"""
Fixers regarding CI.
"""

import os.path
import re
import instarepo.fixers.base
import instarepo.fixers.context
from string import Template


class NoTravisFix:
    """Removes the .travis.yml file"""

    def __init__(self, context: instarepo.fixers.context.Context):
        self.context = context

    def run(self):
        filename = ".travis.yml"
        full_name = self.context.git.join(filename)
        if not os.path.isfile(full_name):
            return []
        self.context.git.rm(filename)
        msg = f"chore: Removed {filename}"
        self.context.git.commit(msg)
        return [msg]


class NoTravisBadgeFix(instarepo.fixers.base.SingleFileFix):
    """Removes the Travis badge from README files"""

    def __init__(self, context: instarepo.fixers.context.Context):
        super().__init__(
            context.git, "README.md", "chore: Removed Travis badge from README"
        )

    def convert(self, contents: str) -> str:
        return remove_travis_badge(contents)


RE_BADGE = re.compile(
    r"\[!\[Build Status\]\(https://travis-ci[^)]+\)\]\(https://travis-ci[^)]+\)"
)


def remove_travis_badge(contents: str) -> str:
    return RE_BADGE.sub("", contents)


class PythonBuildFix(instarepo.fixers.base.MissingFileFix):
    """Adds a build GitHub action for Python projects"""

    def __init__(self, context: instarepo.fixers.context.Context):
        super().__init__(context.git, ".github/workflows/build.yml")
        self.context = context

    def get_contents(self) -> str:
        with open(self.git.join("Pipfile"), "r", encoding="utf-8") as file:
            pipfile_lines = file.readlines()
        has_build_dependency = any(
            filter(lambda line: line.startswith("build"), pipfile_lines)
        )
        if has_build_dependency:
            return """name: Python CI

on:
  push:
    branches: [ trunk ]
  pull_request:
    branches: [ trunk ]

jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.8', '3.9', '3.10']
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v2
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pipenv
          pipenv install --dev
      - name: Test with pytest
        run: |
          pipenv run pytest
      - name: Build wheel
        run: |
          pipenv run python -m build
      - name: Upload wheel
        uses: actions/upload-artifact@v2
        with:
          name: wheel-${{ matrix.python-version }}
          path: dist/*.whl
"""

        return """name: Python CI

on:
  push:
    branches: [ trunk ]
  pull_request:
    branches: [ trunk ]
jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.8', '3.9', '3.10']
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v2
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pipenv
          pipenv install --dev
      - name: Test with pytest
        run: |
          pipenv run pytest
"""

    def should_process_repo(self) -> bool:
        return self.git.isfile("Pipfile")


class PythonReleaseFix(instarepo.fixers.base.MissingFileFix):
    """Adds a release GitHub action for Python projects"""

    def __init__(self, context: instarepo.fixers.context.Context):
        super().__init__(context.git, ".github/workflows/release.yml")
        self.context = context

    def get_contents(self) -> str:
        template = Template(
            """name: Release

on:
  push:
    tags: [ "v*" ]

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pipenv
          pipenv install --dev
      - name: Test with pytest
        run: |
          pipenv run pytest
      - name: Build wheel
        run: |
          pipenv run python -m build
      - name: Publish wheel with twine
        run: >
          pipenv run twine upload
          -u $${{secrets.${twine_username_variable}}}
          -p $${{secrets.${twine_password_variable}}}
          --non-interactive
          --disable-progress-bar
          dist/*
"""
        )
        name = self.context.full_name().split("/")[-1].upper()
        return template.substitute(
            twine_username_variable=f"{name}_TWINE_USERNAME",
            twine_password_variable=f"{name}_TWINE_PASSWORD",
        )

    def should_process_repo(self) -> bool:
        if not self.git.isfile("Pipfile"):
            return False
        with open(self.git.join("Pipfile"), "r", encoding="utf-8") as file:
            pipfile_lines = file.readlines()
        has_twine_dependency = any(
            filter(lambda line: line.startswith("twine"), pipfile_lines)
        )
        return has_twine_dependency
