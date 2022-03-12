"""Unit tests for dotnet.py"""

from .dotnet import (
    get_projects_from_sln_file_contents,
    comment,
    SlnParser,
    csproj_root_node_to_os,
)
import xml.etree.ElementTree as ET
from instarepo.xml_utils import create_parser


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


def test_get_projects_from_sln_file_contents_new_guid():
    """Tests support for the new GUID used by the dotnet CLI"""
    sln_file = """
Microsoft Visual Studio Solution File, Format Version 12.00
# Visual Studio Version 16
VisualStudioVersion = 16.0.29102.190
MinimumVisualStudioVersion = 15.0.26124.0
Project("{9A19103F-16F7-4668-BE54-9A1E7A4F7556}") = "DuplicateFileFinder", "DuplicateFileFinder\DuplicateFileFinder.csproj", "{55E0401D-7FA2-4809-B98F-3D5C1EEEF336}"
EndProject
Project("{9A19103F-16F7-4668-BE54-9A1E7A4F7556}") = "PostfixNumberRemover", "PostfixNumberRemover\PostfixNumberRemover.csproj", "{4884CCE8-C949-41FD-8136-BCCB2AF657E6}"
EndProject
Project("{9A19103F-16F7-4668-BE54-9A1E7A4F7556}") = "PostfixNumberRemover.Tests", "PostfixNumberRemover.Tests\PostfixNumberRemover.Tests.csproj", "{F871B937-163D-400D-9BAC-D49C8BC7A629}"
EndProject"""
    projects = list(get_projects_from_sln_file_contents(sln_file))
    assert projects == [
        "DuplicateFileFinder\\DuplicateFileFinder.csproj",
        "PostfixNumberRemover\\PostfixNumberRemover.csproj",
        "PostfixNumberRemover.Tests\\PostfixNumberRemover.Tests.csproj",
    ]


def test_comment():
    x, y = comment()("# hello")
    assert x == "# hello"
    assert y == ""
    x, y = comment()("# hello\r\n\r\ngood bye")
    assert x == "# hello"
    assert y == "good bye"


def test_sln_parser():
    sln_file = """# Visual Studio 15
VisualStudioVersion = 15.0.27130.2020
MinimumVisualStudioVersion = 10.0.40219.1
Project("{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}") = "CVRender.Web", "CVRender.Web\\CVRender.Web.csproj", "{46D05687-EB9B-4885-9A14-1BDC8BBB253B}"
EndProject"""
    parser = SlnParser(sln_file)
    assert parser.next() == "# Visual Studio 15"
    assert parser.next() == "VisualStudioVersion"
    assert parser.next() == "="
    assert parser.next() == "15.0.27130.2020"
    assert parser.next() == "\n"
    assert parser.next() == "MinimumVisualStudioVersion"
    assert parser.next() == "="
    assert parser.next() == "10.0.40219.1"
    assert parser.next() == "\n"
    assert parser.next() == "Project"
    assert parser.next() == "("
    assert parser.next() == '"{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}"'
    assert parser.next() == ")"
    assert parser.next() == "="
    assert parser.next() == '"CVRender.Web"'
    assert parser.next() == ","
    assert parser.next() == '"CVRender.Web\\CVRender.Web.csproj"'
    assert parser.next() == ","
    assert parser.next() == '"{46D05687-EB9B-4885-9A14-1BDC8BBB253B}"'
    assert parser.next() == "\n"
    assert parser.next() == "EndProject"


def test_parse_msbuild_style_csproj():
    input = """<?xml version="1.0" encoding="utf-8"?>
<Project ToolsVersion="15.0" DefaultTargets="Build" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
</Project>
"""
    root = ET.fromstring(input, create_parser())
    assert csproj_root_node_to_os(root) == "windows"


def test_parse_dotnet_style_csproj():
    input = """<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <TargetFramework>netstandard2.1</TargetFramework>
  </PropertyGroup>
</Project>
"""
    root = ET.fromstring(input, create_parser())
    assert csproj_root_node_to_os(root) == "linux"


def test_parse_dotnet_net47_style_csproj():
    input = """<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <TargetFramework>net47</TargetFramework>
  </PropertyGroup>
</Project>
"""
    root = ET.fromstring(input, create_parser())
    assert csproj_root_node_to_os(root) == "windows"
