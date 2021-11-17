"""Unit tests for dotnet.py"""

from .dotnet import get_projects_from_sln_file_contents


def test_get_projects_from_sln_file_contents():
    """Tests extracting csproj files from sln contents"""
    sln_file = """# Visual Studio 15
VisualStudioVersion = 15.0.27130.2020
MinimumVisualStudioVersion = 10.0.40219.1
Project("{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}") = "CVRender.Web", "CVRender.Web\\CVRender.Web.csproj", "{46D05687-EB9B-4885-9A14-1BDC8BBB253B}"
EndProject
Project("{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}") = "CVRender", "CVRender\\CVRender.csproj", "{BD17C766-DF9E-4117-A8CB-2BAA8FE6D9B9}"
EndProject
Project("{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}") = "CVRender.Tests", "CVRender.Tests\\CVRender.Tests.csproj", "{FDABDD4B-8BF5-4E4A-B977-400D0CE04D4A}"
EndProject
Project("{2150E333-8FDC-42A3-9474-1A3956D46DE8}") = "Solution Items", "Solution Items", "{184005A4-82D4-489E-BD9C-390DFEBC074D}"
	ProjectSection(SolutionItems) = preProject
		.gitignore = .gitignore
		appveyor.yml = appveyor.yml
		LICENSE = LICENSE
		README.md = README.md
	EndProjectSection
EndProject"""
    projects = list(get_projects_from_sln_file_contents(sln_file))
    assert projects == [
        "CVRender.Web\\CVRender.Web.csproj",
        "CVRender\\CVRender.csproj",
        "CVRender.Tests\\CVRender.Tests.csproj",
    ]
