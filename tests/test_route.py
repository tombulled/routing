import arguments

from routing.models import Route


def test_matches_no_args() -> None:
    route: Route = Route("foo")

    assert route.matches(route.path)
    assert not route.matches("bar")


def test_matches_args() -> None:
    route: Route = Route("foo {} {kwarg}")

    assert route.matches("foo 123 abc")
    assert not route.matches("bar")


def test_match_no_args() -> None:
    route: Route = Route("foo")

    assert route.match("foo") == arguments.Arguments()
    assert route.match("bar") is None

def test_match_args() -> None:
    route: Route = Route("foo {} {kwarg}")

    assert route.match("foo 123 abc") == arguments.Arguments("123", kwarg="abc")
    assert route.match("bar") is None