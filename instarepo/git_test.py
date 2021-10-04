from pytest_mock import MockerFixture
import instarepo.git


def test_clone(mocker: MockerFixture) -> None:
    mock = mocker.patch("subprocess.run")
    instarepo.git.clone("ssh://hello.git", "/tmp/hello")
    mock.assert_called_once_with(
        ["git", "clone", "ssh://hello.git", "/tmp/hello"], check=True
    )
