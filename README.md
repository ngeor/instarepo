# instarepo

CLI automation tool to batch process multiple repositories.

## Requirements

Requirements:

- python 3.8+
- pipenv

Install dependencies with `pipenv install --dev`

## Usage

Inside a pipenv shell, run: `python -m instarepo.main`

```
$ python -m instarepo.main --help
usage: main.py [-h] -u USER -t TOKEN [--repo-prefix REPO_PREFIX] [--verbose] [--forks | --no-forks]
               [--sort {full_name,created,updated,pushed}] [--direction {asc,desc}]
               {analyze,list,fix} ...

Apply changes on multiple repositories

positional arguments:
  {analyze,list,fix}    Sub-commands help
    analyze             Analyzes the available repositories, counting historical LOC
    list                Lists the available repositories
    fix                 Runs automatic fixes on the repositories

optional arguments:
  -h, --help            show this help message and exit
  -u USER, --user USER  The GitHub username
  -t TOKEN, --token TOKEN
                        The GitHub token
  --repo-prefix REPO_PREFIX
                        Only process repositories whose name starts with the given prefix
  --verbose             Verbose output
  --forks, --no-forks   Process forks (default: True)
  --sort {full_name,created,updated,pushed}
  --direction {asc,desc}
```

## Analyze

Analyzes repositories.

```
usage: main.py analyze [-h] --since SINCE [--metric {commits,files}]

optional arguments:
  -h, --help            show this help message and exit
  --since SINCE         The start date of the analysis (YYYY-mm-dd)
  --metric {commits,files}
                        The metric to report on
```

## Fix

Applies automatic fixes on repositories.

instarepo will:

- clone all your GitHub repositories in a temporary local folder
- process all non-archived repositories and apply automatic fixes
- create a merge request for every repository that had changes

```
usage: main.py fix [-h] [--dry-run]

Runs automatic fixes on the repositories

optional arguments:
  -h, --help  show this help message and exit
  --dry-run   Do not actually push and create MR
```

### Fixes

#### Generic

- `must_have_editorconfig`: Ensures the repo has a `.editorconfig` file.
- `must_have_github_funding`: Adds a funding yaml for GitHub
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

#### Dot Net

- `dot_net_framework_version`: Ensures csproj and `web.config` files
  target the desired version of .NET framework.
- `must_have_csharp_app_veyor`: Adds an `appveyor.yml` file to .NET C# solutions.

#### Maven

- `maven`: Uses the version plugin to update dependencies.
  Requires maven to be installed. Dependecies are updated with
  [update-parent](https://www.mojohaus.org/versions-maven-plugin/update-parent-mojo.html),
  [update-properties](https://www.mojohaus.org/versions-maven-plugin/update-properties-mojo.html),
  and [use-latest-releases](https://www.mojohaus.org/versions-maven-plugin/use-latest-releases-mojo.html).
  Major version updates are not allowed. Versions with patterns like `Beta` are not allowed.
- `must_have_maven_github_workflow`: For projects that have a `pom.xml`, ensures a GitHub Actions workflow
  that builds the project
- `must_have_maven_gitignore`: For Maven projects (that have a `pom.xml`), adds
  a `.gitignore` file copied from https://github.com/github/gitignore/blob/master/Maven.gitignore

#### Pascal

- `autoformat`: Autoformats Pascal source code with [JEDI Code Format](http://jedicodeformat.sourceforge.net/).
  Prerequisites:
  - The `JFC.exe` is located at `C:\opt\jcf_243_exe\JCF.exe`
  - The configuration file is located at `%LOCALAPPDATA%\lazarus\jcfsettings.cfg`
- `must_have_lazarus_gitignore`: For Lazarus projects, adds a `.gitignore` file

## List

Lists the repositories.
