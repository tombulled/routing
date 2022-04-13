import pytest
from routing.models import Mount


@pytest.fixture
def path() -> str:
    return "path"


def test_mount_lhs(path: str) -> None:
    mount: Mount = Mount(
        path="mount",
        sep="/",
        suffix=False,
    )

    assert mount.apply(path) == "mount/path"


def test_mount_rhs(path: str) -> None:
    mount: Mount = Mount(
        path="mount",
        sep="/",
        suffix=True,
    )

    assert mount.apply(path) == "path/mount"
