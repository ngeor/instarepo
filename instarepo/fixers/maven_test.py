"""Unit tests for maven.py"""
import xml.etree.ElementTree as ET

import instarepo.xml_utils
from .maven import javadoc_badge


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
