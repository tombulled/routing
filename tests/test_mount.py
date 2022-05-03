from routing.models import Mount


def test_apply() -> None:
    assert Mount(path="path", suffix=False).apply("string", sep="/") == "path/string"
    assert Mount(path="path", suffix=True).apply("string", sep="/") == "string/path"
