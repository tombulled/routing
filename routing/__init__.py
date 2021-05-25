import pydantic
import attr
import collections
import parse
import addict

import functools

from typing import List, Dict, Set, Optional
import typing as t

'''
TODO:
    * Implement <Mount>
'''

class NotFound(Exception): pass
class MethodNotAllowed(Exception): pass

class RouterError(Exception): pass

class Request(pydantic.BaseModel):
    path:   str
    params: Optional[addict.Dict]

class HttpRequest(Request):
    method: str

class Target(object):
    def __init__(self, data):
        self.data = data

    def __call__(self, request):
        return self.data

class Path(collections.UserString):
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.data!r})'

    # def __hash__(self) -> str:
    #     return hash(self.reduce())

    def __eq__(self, rhs: str) -> bool:
        return str.__eq__(self.reduce(), self.__class__.reduce(rhs))

    def reduce(self) -> str:
        parser = parse.compile(str(self))

        return self.format(** dict.fromkeys(parser.named_fields, str(dict())))

    def parse(self, path: str):
        return (result := parse.parse(self.data, path)) and result.named

class AnyPath(Path):
    def __init__(self):
        super().__init__('*')

    def __repr__(self) -> str:
        return 'Path(*)'

    # def __hash__(self) -> str:
    #     return hash(self.data)

    def __eq__(self, rhs: str) -> bool:
        return True

@attr.s(auto_attribs = True)
class Route(object):
    path:   Path = attr.ib(converter = lambda path: path if isinstance(path, Path) else Path(path))
    target: t.Callable

    def matches(self, path: Optional[str]):
        return self.path == path or (path is not None and self.path.parse(path) is not None)

@attr.s
class Router(object):
    routes: t.List[Route] = attr.ib(default=attr.Factory(list))

    def __call__(self, path: Optional[str] = None):
        route = self.resolve(path)

        request = Request \
        (
            path   = path,
            params = params if (params := route.path.parse(path)) is None else addict.Dict(params),
        )

        return route.target(request)

    def __getattr__(self, path: str):
        if path.startswith('_'):
            raise AttributeError

        return self.route(path)

    def resolve(self, path: str):
        for route in self.routes:
            if route.matches(path):
                return route

        raise NotFound(path)

    def route(self, *paths: str):
        def decorator(target: t.Any = None):
            for path in paths:
                if isinstance(target, self.__class__):
                    for route in target.routes:
                        self.routes.append \
                        (
                            Route \
                            (
                                path   = path + route.path,
                                target = route.target,
                            ),
                        )
                else:
                    self.routes.append \
                    (
                        Route \
                        (
                            path   = path,
                            target = target,
                        ),
                    )

            return target

        return decorator

@attr.s(auto_attribs = True)
class HttpMethodRouter(Router):
    def resolve(self, path: str):
        try:
            return super().resolve(path)
        except NotFound:
            raise MethodNotAllowed(path) from None

@attr.s
class HttpRoute(Route):
    target: HttpMethodRouter = attr.ib(default=attr.Factory(HttpMethodRouter))

    def __call__(self, method: t.Optional[str] = None):
        return self.target(method)

    @property
    def any(self):
        return self.target.route(AnyPath())

    def __getattr__(self, method: str):
        return getattr(self.target, method)

class HttpRouter(Router):
    routes: t.List[HttpRoute] = attr.ib(default=attr.Factory(list))

    def __call__(self, path: str, method: Optional[str] = None):
        route = self.resolve(path)

        route_method = route.resolve(method)

        request = HttpRequest \
        (
            path   = path,
            params = params if (params := route.path.parse(path)) is None else addict.Dict(params),
            method = method,
        )

        return route_method.target(request)

    def __getattr__(self, method: str):
        if method.startswith('_'):
            raise AttributeError

        return functools.partial(self.route, methods={method})

    def any(self, *paths: str):
        return self.route(*paths, methods = {AnyPath()})

    def route(self, *paths: str, methods: Optional[Set[str]] = None):
        def decorator(target: t.Any = None):
            for path in paths:
                route = HttpRoute \
                (
                    path = path,
                )

                for method in methods or (AnyPath(),):
                    route.target.route(method)(target)

                self.routes.append(route)

            return target

        return decorator
