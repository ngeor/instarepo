from .maven import filter_maven_output

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
