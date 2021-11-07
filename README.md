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
usage: main.py [-h] [--verbose] {list,fix,analyze} ...

Apply changes on multiple repositories

positional arguments:
  {list,fix,analyze}  Sub-commands help
    list              Lists the available repositories
    fix               Runs automatic fixes on the repositories
    analyze           Analyzes the available repositories, counting historical LOC

optional arguments:
  -h, --help          show this help message and exit
  --verbose           Verbose output
```

## List

Lists the repositories.

By default, skips forks and archived repositories.

```
usage: main.py list [-h] -u USER -t TOKEN [--sort {full_name,created,updated,pushed}] [--direction {asc,desc}]
                    [--only-language ONLY_LANGUAGE | --except-language EXCEPT_LANGUAGE]
                    [--only-name-prefix ONLY_NAME_PREFIX | --except-name-prefix EXCEPT_NAME_PREFIX]
                    [--forks {allow,deny,only}] [--archived {allow,deny,only}]

optional arguments:
  -h, --help            show this help message and exit
  --only-language ONLY_LANGUAGE
                        Only process repositories of the given programming language
  --except-language EXCEPT_LANGUAGE
                        Do not process repositories of the given programming language
  --only-name-prefix ONLY_NAME_PREFIX
                        Only process repositories whose name starts with the given prefix
  --except-name-prefix EXCEPT_NAME_PREFIX
                        Do not process repositories whose name starts with the given prefix
  --archived {allow,deny,only}
                        Filter archived repositories

Authentication:
  -u USER, --user USER  The GitHub username
  -t TOKEN, --token TOKEN
                        The GitHub token

Sorting:
  --sort {full_name,created,updated,pushed}
  --direction {asc,desc}

Filtering:
  --forks {allow,deny,only}
                        Filter forks

Example:
    pipenv run python -m instarepo.main list -u USER -t TOKEN
```

## Fix

Applies automatic fixes on repositories.

instarepo will:

- clone all your GitHub repositories in a temporary local folder
- process all non-archived repositories and apply automatic fixes
- create a merge request for every repository that had changes

By default skips forks. It's not possible to select archived repositories, as they are read-only.

```
usage: main.py fix [-h] -u USER -t TOKEN [--sort {full_name,created,updated,pushed}] [--direction {asc,desc}]
                   [--only-language ONLY_LANGUAGE | --except-language EXCEPT_LANGUAGE]
                   [--only-name-prefix ONLY_NAME_PREFIX | --except-name-prefix EXCEPT_NAME_PREFIX]
                   [--forks {allow,deny,only}] [--dry-run]

Runs automatic fixes on the repositories

optional arguments:
  -h, --help            show this help message and exit
  --only-language ONLY_LANGUAGE
                        Only process repositories of the given programming language
  --except-language EXCEPT_LANGUAGE
                        Do not process repositories of the given programming language
  --only-name-prefix ONLY_NAME_PREFIX
                        Only process repositories whose name starts with the given prefix
  --except-name-prefix EXCEPT_NAME_PREFIX
                        Do not process repositories whose name starts with the given prefix
  --dry-run             Do not actually push and create MR

Authentication:
  -u USER, --user USER  The GitHub username
  -t TOKEN, --token TOKEN
                        The GitHub token

Sorting:
  --sort {full_name,created,updated,pushed}
  --direction {asc,desc}

Filtering:
  --forks {allow,deny,only}
                        Filter forks

Example:
    pipenv run python -m instarepo.main fix -u USER -t TOKEN

Fixers:

dotnet.dot_net_framework_version_fix
    Sets the .NET Framework version to 4.7.2 in csproj and web.config files
dotnet.must_have_c_sharp_app_veyor
    If missing, creates an appveyor.yml file for CSharp projects
license.copyright_year_fix
    Ensures the year in the license file copyright is up to date
license.must_have_license_fix
    Ensures that a license file exists
maven.maven_fix
    Updates the dependencies of a Maven project
maven.must_have_maven_git_hub_workflow
    If missing, adds a GitHub action Maven build workflow
maven.must_have_maven_git_ignore
    If missing, adds a .gitignore file for Maven projects
missing_files.must_have_readme_fix
    Ensures that the repo has a readme file
missing_files.must_have_editor_config_fix
    Ensures an editorconfig file exists
missing_files.must_have_git_hub_funding_fix
    Ensures a GitHub funding file exists
pascal.auto_format
    Automatically formats Pascal files with JEDI code format
pascal.must_have_lazarus_git_ignore
    If missing, adds a gitignore file for Lazarus projects
readme_image.readme_image_fix

    Finds broken images in the `README.md` file.
    Able to correct images that were moved one or more
    folders up but the user forgot to update them in the `README.md` file.

repo_description.repo_description_fix

    Updates GitHub's repo description based on the README file.

    Note: this fixer does not create an MR, it calls the
    GitHub REST API directly (https://docs.github.com/en/rest/reference/repos#update-a-repository).

vb6.must_have_git_ignore
    If mising, adds a gitignore file for VB6 projects
```

### Fixes

#### Generic

- `copyright_year`: Updates the copyright year in `LICENSE` file.
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

#### VB6

- `must_have_vb6_gitignore`: For Visual Basic projects and project groups,
  adds a `.gitignore` file


## Analyze

Analyzes repositories.

By default, skips forks and archived repositories.

```
usage: main.py analyze [-h] -u USER -t TOKEN [--sort {full_name,created,updated,pushed}] [--direction {asc,desc}]
                       [--only-language ONLY_LANGUAGE | --except-language EXCEPT_LANGUAGE]
                       [--only-name-prefix ONLY_NAME_PREFIX | --except-name-prefix EXCEPT_NAME_PREFIX]
                       [--forks {allow,deny,only}] [--archived {allow,deny,only}] --since SINCE
                       [--metric {commits,files}]

optional arguments:
  -h, --help            show this help message and exit
  --only-language ONLY_LANGUAGE
                        Only process repositories of the given programming language
  --except-language EXCEPT_LANGUAGE
                        Do not process repositories of the given programming language
  --only-name-prefix ONLY_NAME_PREFIX
                        Only process repositories whose name starts with the given prefix
  --except-name-prefix EXCEPT_NAME_PREFIX
                        Do not process repositories whose name starts with the given prefix
  --archived {allow,deny,only}
                        Filter archived repositories
  --since SINCE         The start date of the analysis (YYYY-mm-dd)
  --metric {commits,files}
                        The metric to report on

Authentication:
  -u USER, --user USER  The GitHub username
  -t TOKEN, --token TOKEN
                        The GitHub token

Sorting:
  --sort {full_name,created,updated,pushed}
  --direction {asc,desc}

Filtering:
  --forks {allow,deny,only}
                        Filter forks

Example:
    pipenv run python -m instarepo.main analyze -u USER -t TOKEN --since 2021-11-06
```
