# instarepo

CLI automation tool to apply automatic changes on multiple repositories.

## Overview

instarepo will:

- clone all your GitHub repositories in a temporary local folder
- process all non-archived repositories and apply automatic fixes
- create a merge request for every repository that had changes

## Fixes

- `must_have_license`: Ensures the repo has a `LICENSE` file.
  Only runs for public repositories.
  Adds the MIT License. The copyright owner is populated by
  `git config user.name`.
- `must_have_readme`: Ensures the repo has a `README.md` file.
- `readme_image`: Attempts to detect and correct broken image links
  inside the `README.md` file of your repo. Detects only images that
  got moved from a subfolder into a parent folder (e.g. `/folder/photo.png`
  that got moved to `/photo.png`).
- `repo_description`: Updates the description of a GitHub repository
  based on the `README.md` file. This fixer does _not_ create a MR,
  instead it calls GitHub's REST API directly to change the metadata
  of the repo. The description is the first line of the README file
  that starts with a letter or with `>`.

## Requirements

Requirements:

- python 3.8+
- pipenv

Install dependencies with `pipenv install --dev`

## Usage

Inside a pipenv shell, run: `python -m instarepo.main`

```
$ python -m instarepo.main --help
usage: main.py [-h] -u USER -t TOKEN [--dry-run] [--sample] [--verbose]

Apply changes on multiple repositories

optional arguments:
  -h, --help            show this help message and exit
  -u USER, --user USER  The GitHub username
  -t TOKEN, --token TOKEN
                        The GitHub token
  --dry-run             Do not actually push and create MR
  --sample              Do not process all repositories, just one
  --verbose             Verbose output
```
