from typing import Any

import routing
from routing import api


def test_get_routes() -> None:
    @routing.route("/foo")
    def function(*args: Any, **kwargs: Any) -> None:
        ...

    @routing.route("/foo")
    class CallableClass:
        def __call__(self, *args: Any, **kwargs: Any) -> None:
            ...

    class Class:
        @routing.route("/foo")
        def method(self, *args: Any, **kwargs: Any) -> None:
            ...

    callable_cls: CallableClass = CallableClass()
    cls: Class = Class()

    assert api.get_routes(function) == [routing.Route("/foo", target=function)]
    assert api.get_routes(CallableClass) == [
        routing.Route("/foo", target=CallableClass)
    ]
    assert api.get_routes(callable_cls) == [routing.Route("/foo", target=callable_cls)]
    assert api.get_routes(Class) == [routing.Route("/foo", target=Class.method)]
    assert api.get_routes(cls) == [routing.Route("/foo", target=cls.method)]


def test_get_middleware() -> None:
    @routing.middleware
    def function(*args: Any, **kwargs: Any) -> None:
        ...

    @routing.middleware
    class CallableClass:
        def __call__(self, *args: Any, **kwargs: Any) -> None:
            ...

    class Class:
        @routing.middleware
        def method(self, *args: Any, **kwargs: Any) -> None:
            ...

    callable_cls: CallableClass = CallableClass()
    cls: Class = Class()

    assert api.get_middleware(function) == [function]
    assert api.get_middleware(CallableClass) == [CallableClass]
    assert api.get_middleware(callable_cls) == [callable_cls]
    assert api.get_middleware(Class) == [Class.method]
    assert api.get_middleware(cls) == [cls.method]


def test_router() -> None:
    @routing.route('route_1')
    def route_1(*args: Any, **kwargs: Any) -> None:
        ...

    @routing.middleware
    def middleware_1(*args: Any, **kwargs: Any) -> None:
        ...

    sub_router: routing.Router = routing.Router()

    @sub_router.route('route_2')
    def route_2(*args: Any, **kwargs: Any) -> None:
        ...

    @sub_router.middleware
    def middleware_2(*args: Any, **kwargs: Any) -> None:
        ...

    router: routing.Router = api.router(route_1, middleware_1, sub_router)

    assert router.routes == [
        routing.Route("route_1", target=route_1),
        routing.Route("route_2", target=route_2),
    ]
    assert router.middlewares == [middleware_1, middleware_2]