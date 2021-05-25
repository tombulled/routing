import pydantic
import attr
import collections
import parse
import addict

import functools
import operator

from typing import List, Dict, Set, Optional, Callable
import typing as t

from . import errors
from . import mixins

class Request(pydantic.BaseModel):
    path:   str
    params: addict.Dict = pydantic.Field(default_factory = addict.Dict)

    def copy(self, **kwargs):
        return super().copy(update = kwargs)

    def render(self) -> str:
        return self.path.format(** self.params)

class HttpRequest(Request):
    method: str

@attr.s
class Target(object):
    data: t.Any = attr.ib(default = None)

    def __call__(self, request: Request) -> t.Any:
        return self.data

class Path(str):
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({super().__repr__()})'

    def __invert__(self):
        return self.reduce()

    def reduce(self) -> str:
        return self.format(** dict.fromkeys(parse.compile(self).named_fields, str(dict())))

    def parse(self, path: str, **kwargs) -> Optional[dict]:
        return (result := parse.parse(self, path, **kwargs)) and result.named

    def matches(self, path: str, **kwargs) -> bool:
        return self.parse(path, **kwargs) is not None

    def reductively_equals(self, path: 'Path', case_sensitive: bool = True):
        operands = map(self.__class__.reduce, (self, path))

        if not case_sensitive:
            operands = map(self.__class__.lower, operands)

        return operator.eq(*operands)

class AnyPath(Path):
    def __init__(self):
        super().__init__('*')

    def __repr__(self) -> str:
        return 'Path(*)'

    def __eq__(self, rhs: str) -> bool:
        return True

@attr.s(auto_attribs = True)
class Route(object):
    path:   Path = attr.ib(converter = lambda path: path if isinstance(path, Path) else Path(path))
    target: t.Callable

@attr.s
class Router(object):
    routes:         List[Route] = attr.ib(default = attr.Factory(list))
    case_sensitive: bool        = attr.ib(default = False)

    def __call__(self, path: Optional[str] = None):
        route = self.resolve(path)

        request = self.build(route, path)

        return route.target(request)

    def build(self, route, path: str):
        return Request \
        (
            path   = path,
            params = \
            (
                params
                if (params := route.path.parse(path, case_sensitive = self.case_sensitive)) is None
                else addict.Dict(params)
            ),
        )

    def __getattr__(self, path: str):
        if path.startswith('_'):
            raise AttributeError

        return self.route(path)

    def resolve(self, path: str):
        for route in self.routes:
            if route.path.matches(path, case_sensitive = self.case_sensitive):
                return route

        raise errors.NotFound(path)

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
        except errors.NotFound:
            raise errors.MethodNotAllowed(path) from None

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

@attr.s
class HttpRouter(Router):
    routes: t.List[HttpRoute] = attr.ib(default=attr.Factory(list))

    def __call__(self, path: str, method: Optional[str] = None):
        route = self.resolve(path)

        route_method = route.resolve(method)

        request = self.build \
        (
            route,
            path   = path,
            method = method,
        )

        return route_method.target(request)

    def build(self, route, path: str, method: str):
        return HttpRequest \
        (
            path   = path,
            params = params if (params := route.path.parse(path)) is None else addict.Dict(params),
            method = method,
        )

    def __getattr__(self, method: str):
        if method.startswith('_'):
            raise AttributeError

        return functools.partial(self.route, methods={method})

    def any(self, *paths: str):
        return self.route(*paths, methods = None)

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

class InverseRouter(mixins.InverseRouterMixin, Router): pass
class InverseHttpRouter(mixins.InverseRouterMixin, HttpRouter): pass
