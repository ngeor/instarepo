"""Unit tests for maven.py"""
import xml.etree.ElementTree as ET

import instarepo.xml_utils
from .maven import filter_maven_output, javadoc_badge


def test_filter_maven_output():
    output = """[INFO] Scanning for projects...
[INFO]
[INFO] -------------< com.github.ngeor:archetype-quickstart-jdk8 >-------------
[INFO] Building archetype-quickstart-jdk8 2.9.0-SNAPSHOT
[INFO] --------------------------[ maven-archetype ]---------------------------
[INFO]
[INFO] --- versions-maven-plugin:2.7:update-parent (default-cli) @ archetype-quickstart-jdk8 ---
[INFO] artifact com.github.ngeor:java: checking for updates from central
[INFO] Downloading from central: https://repo.maven.apache.org/maven2/com/github/ngeor/java/2.0.0/java-2.0.0.pom
[INFO] Downloaded from central: https://repo.maven.apache.org/maven2/com/github/ngeor/java/2.0.0/java-2.0.0.pom (13 kB at 57 kB/s)
[INFO] Updating parent from 1.10.0 to 2.0.0
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
[INFO] Total time:  6.119 s
[INFO] Finished at: 2021-10-10T09:50:07+02:00
[INFO] ------------------------------------------------------------------------
"""
    expected_output = "Updating parent from 1.10.0 to 2.0.0"
    actual_output = filter_maven_output(output)
    assert actual_output == expected_output


def test_detect_javadoc_usage_in_pom():
    contents = """<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.github.ngeor</groupId>
  <artifactId>yak4j-spring-test-utils</artifactId>
  <version>0.22.0-SNAPSHOT</version>
  <name>yak4j-spring-test-utils</name>
  <build>
    <plugins>
      <plugin>
        <artifactId>maven-checkstyle-plugin</artifactId>
        <version>3.1.2</version>
        <executions>
          <execution>
            <id>validate</id>
            <phase>validate</phase>
            <goals>
              <goal>check</goal>
            </goals>
          </execution>
        </executions>
      </plugin>
      <plugin>
        <artifactId>maven-source-plugin</artifactId>
        <version>3.2.1</version>
        <executions>
          <execution>
            <id>attach-sources</id>
            <goals>
              <goal>jar-no-fork</goal>
            </goals>
          </execution>
        </executions>
      </plugin>
      <plugin>
        <artifactId>maven-javadoc-plugin</artifactId>
        <version>3.1.1</version>
        <executions>
          <execution>
            <id>attach-javadocs</id>
            <goals>
              <goal>jar</goal>
            </goals>
          </execution>
        </executions>
      </plugin>
      <plugin>
        <artifactId>maven-surefire-plugin</artifactId>
        <version>3.0.0-M5</version>
        <executions>
          <execution>
            <id>default-test</id>
            <phase>test</phase>
            <goals>
              <goal>test</goal>
            </goals>
          </execution>
        </executions>
      </plugin>
    </plugins>
  </build>
</project>
    """
    root = ET.fromstring(contents, parser=instarepo.xml_utils.create_parser())
    assert root is not None
    badges = javadoc_badge(root)
    assert badges == {
        "javadoc": "[![javadoc](https://javadoc.io/badge2/com.github.ngeor/yak4j-spring-test-utils/javadoc.svg)](https://javadoc.io/doc/com.github.ngeor/yak4j-spring-test-utils)"
    }
