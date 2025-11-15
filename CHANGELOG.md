## [unreleased]

### 🎨 Styling

- Styling changelog according to default options

### ⚙️ Miscellaneous Tasks

- Removed funding file
- Updated github workflow
- Upgraded dependencies
- Removed .gitattributes
## [0.14.0] - 2022-03-18

### 🚀 Features

- Use custom author name, start from scratch if all commits are from instarepo (Fixes #54)
## [0.13.0] - 2022-03-18

### 🚀 Features

- Projects-dir parameter of clone should default to current directory (Fixes #48)
- Ability to overwrite certain files

### ⚙️ Miscellaneous Tasks

- Added script to auto-generate README file
- Removed pre-release support
## [0.12.0] - 2022-03-12

### 🚀 Features

- Fixers for adding Python build and release workflows

### 🐛 Bug Fixes

- Support older (msbuild) style csproj files
## [0.11.2] - 2022-03-06

### 🐛 Bug Fixes

- [**breaking**] Use config file to look up cliff.toml
## [0.11.1] - 2022-03-06

### 🐛 Bug Fixes

- Avoid crash for old .NET projects
## [0.11.0] - 2022-03-05

### 🚀 Features

- Implemented config file support (#49) (Fixes #35)
- Dotnet.must_have_git_hub_action can now run locally too (Fixes #43)
- [**breaking**] Removed rule "dotnet.dot_net_framework_version"
- [**breaking**] Renamed dotnet.must_have_git_hub_action to dotnet.must_have_ci and maven.must_have_maven_git_hub_workflow to maven.must_have_ci
- Support pipeline for Windows .NET projects

### 🐛 Bug Fixes

- Support parsing dotnet projects created by dotnet CLI
## [0.10.1] - 2022-02-20

### 🐛 Bug Fixes

- *(CI)* Removed obsolete script

### ⚙️ Miscellaneous Tasks

- Releasing through CI
## [0.10.0] - 2022-02-19

### 🐛 Bug Fixes

- [**breaking**] Removed the generate changelog fixer because it is spammy

### ⚙️ Miscellaneous Tasks

- Single-sourcing the version
## [0.9.0] - 2022-02-15

### 🚀 Features

- [**breaking**] Only auto-merge PRs when a flag is given
## [0.8.1] - 2022-02-14

### 🐛 Bug Fixes

- Fixed broken tests
- Do not merge MRs with failed builds

### ⚙️ Miscellaneous Tasks

- *(changelog)* Updated changelog
## [0.8.0] - 2022-02-13

### 🚀 Features

- [**breaking**] Using GitHub Actions also for .NET projects
## [0.7.0] - 2022-02-13

### 🚀 Features

- Auto-closing MRs that no longer have changes
- Auto-merge MRs

### ⚙️ Miscellaneous Tasks

- Use a dedicated dependencies group in changelog, sort commits alphabetically
## [0.6.0] - 2022-02-11

### 🚀 Features

- When sorting by a date field, show that date in the last column of the List command
- [**breaking**] Retire maven fixer

### ⚙️ Miscellaneous Tasks

- Added PyPI badge in README
- Added release procedure in README
- *(changelog)* Updated changelog
## [0.5.0] - 2022-02-05

### 🚀 Features

- Building wheel in GitHub Actions
- Publish wheel as artifact in GitHub Actions
- Add  option

### 🐛 Bug Fixes

- Wheel was lacking xml data files
- Badges Maven fixer should not run for local repos

### ⚙️ Miscellaneous Tasks

- *(changelog)* Updated changelog
- Implement setuptools packaging
- *(changelog)* Updated changelog
- Setting 2 space indentation for yaml files
- *(changelog)* Updated changelog
- *(changelog)* Update changelog for 0.5.0
## [0.4.0] - 2022-02-04

### 🚀 Features

- *(CI)* Adding GitHub actions workflow
- Sorting by pushed date instead of updated date in list command
- Adding new clone command that supports cloning GitHub repos
- Store GitHub credentials for easier use
- Support login/logout commands for Linux/Mac
- Ensure changelog is generated last
- Applying fixes to local git repositories

### 🐛 Bug Fixes

- *(CI)* Targetting Python 3.10
- Support Python 3.8
- Excluding alpha versions in Maven upgrades
- Excluding license and repo_description rules from local git repo execution

### ⚙️ Miscellaneous Tasks

- *(CI)* Adding GitHub action badge
- Compatibility issue with Python 3.8
- *(changelog)* Updated changelog
- *(changelog)* Updated changelog
- *(changelog)* Updated changelog
## [0.3.0] - 2022-01-30

### 🚀 Features

- Add git-cliff support
- Use funding.yml from user-templates
## [0.2.0] - 2022-01-29

### 🚀 Features

- Pretty print list output
- Use conventional commit messages
- Using git-cliff to generate changelog
- If Maven output consists of a single version update, add a single line commit
- Allow filtering repos based on when they had changes pushed to them

### ⚙️ Miscellaneous Tasks

- Updated copyright year in LICENSE
## [0.1.0] - 2021-11-17

### 💼 Other

- Using os.linesep causes an issue in the MR
## [2021-03-10-multirepo] - 2020-10-18
