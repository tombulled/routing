import pytest
import annotate
from routing import Router, Route
import routing.sentinels


@pytest.fixture
def router() -> Router:
    return Router()


def test_middleware(router: Router):
    @router.middleware
    def middleware(*args, **kwargs):
        ...

    assert router.middlewares == [middleware]
    assert routing.sentinels.Middleware in annotate.get_annotations(middleware)


def test_route(router: Router):
    @router.route("/foo")
    def foo(*args, **kwargs):
        ...

    route: Route = Route(path="/foo", target=foo)

    assert router.routes == [route]
    assert annotate.get_annotations(foo).get(routing.sentinels.Route) == [route]
