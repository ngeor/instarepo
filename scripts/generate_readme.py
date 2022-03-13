#!/usr/bin/env python3

import os.path
import re
import subprocess


def generate_readme():
    template_filename = os.path.join(os.path.dirname(__file__), "README.md.template")
    with open(template_filename, "r", encoding="utf-8") as file:
        contents = file.read()
    contents = re.sub(r"\${{([^}]+)}}", runner, contents)
    with open("README.md", "w", encoding="utf-8") as file:
        file.write(contents)


def runner(match):
    command_line = match.group(1)
    parts = command_line.split(" ")
    result = subprocess.run(parts, check=True, stdout=subprocess.PIPE, encoding="utf-8")
    return result.stdout.strip()


if __name__ == "__main__":
    generate_readme()
