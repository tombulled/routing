import attr
import addict

import functools
import operator

from typing import List, Dict, Set, Optional, Callable, Union
import typing as t

from . import errors
from . import mixins
from . import types
from . import middleware


@attr.s(kw_only=True)
class Request(object):
    path: types.Path = attr.ib(converter=types.Path)
    params: addict.Dict = attr.ib(
        default=attr.Factory(addict.Dict), converter=addict.Dict
    )

    def copy(self, **kwargs):
        return self.__class__(
            **{
                **attr.asdict(self),
                **kwargs,
            },
        )

    def render(self) -> str:
        return self.path.format(**self.params)


@attr.s(kw_only=True)
class HttpRequest(Request):
    method: str = attr.ib()


@attr.s
class Target(object):
    data: t.Any = attr.ib(default=None)

    def __call__(self, request: t.Optional[Request] = None) -> t.Any:
        return self.data


@attr.s(auto_attribs=True)
class Route(object):
    path: types.Path = attr.ib(converter=types.Path)
    target: t.Callable


@attr.s
class Router(object):
    routes: List[Route] = attr.ib(default=attr.Factory(list))
    case_sensitive: bool = attr.ib(default=False)

    # Note: Make sure doesn't collide with .middleware
    # _middleware: List[t.Callable] = attr.ib(default = attr.Factory(list))
    _middleware: List[t.Callable] = attr.ib(default=[middleware.parametrise])

    request_class: type = attr.ib(default=Request)

    def __call__(self, routable: t.Union[str, Request], **kwargs):
        path = routable if isinstance(routable, str) else routable.render()

        route = self.resolve(path)

        request = (
            routable
            if isinstance(routable, Request)
            else self.build(route, path, **kwargs)
        )

        return self.dispatch(route, request)

    def dispatch(self, route, request):
        call_next = route.target

        # Note: Should this be reversed?
        # for middleware in reversed(self._middleware):
        for middleware in self._middleware:
            call_next = functools.partial(middleware, call_next=call_next)

        return call_next(request)

    def build(self, route, path: str, **kwargs):
        return self.request_class(
            # path   = path,
            path=route.path,
            params=(
                params
                if (
                    params := route.path.parse(path, case_sensitive=self.case_sensitive)
                )
                is None
                else addict.Dict(params)
            ),
            **kwargs,
        )

    def __getattr__(self, path: str):
        if path.startswith("_"):
            raise AttributeError

        return self.route(path)

    def resolve(self, path: str):
        for route in self.routes:
            if route.path.matches(path, case_sensitive=self.case_sensitive):
                return route

        raise errors.NotFound(path)

    def route(self, *paths: str):
        def decorator(target: t.Any = None):
            for path in paths:
                if isinstance(target, self.__class__):
                    for route in target.routes:
                        self.routes.append(
                            Route(
                                path=path + route.path,
                                target=route.target,
                            ),
                        )
                else:
                    self.routes.append(
                        Route(
                            path=path,
                            target=target,
                        ),
                    )

            return target

        return decorator

    def middleware(self, func: t.Callable):
        self._middleware.append(func)

        return func


@attr.s
class HttpMethodRouter(Router):
    _middleware: List[t.Callable] = attr.ib(default=attr.Factory(list))

    def __call__(self, routable: t.Union[str, HttpRequest], **kwargs):
        method = routable if isinstance(routable, str) else routable.method

        return super().__call__(method)

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
        return self.target.route(str(dict()))

    def __getattr__(self, method: str):
        return getattr(self.target, method)


@attr.s
class HttpRouter(Router):
    routes: t.List[HttpRoute] = attr.ib(default=attr.Factory(list))

    # def __call__(self, path: str, method: Optional[str] = None):
    #     route = self.resolve(path)
    #
    #     route_method = route.resolve(method)
    #
    #     request = self.build \
    #     (
    #         route,
    #         path   = path,
    #         method = method,
    #     )
    #
    #     return route_method.target(request)

    request_class: type = attr.ib(default=HttpRequest)

    def dispatch(self, route, request):
        sub_route = route.target.resolve(request.method)

        return super().dispatch(sub_route, request)

    # def build(self, route, path: str, method: str):
    #     return HttpRequest \
    #     (
    #         path   = path,
    #         params = params if (params := route.path.parse(path)) is None else addict.Dict(params),
    #         method = method,
    #     )

    def __getattr__(self, method: str):
        if method.startswith("_"):
            raise AttributeError

        return functools.partial(self.route, methods={method})

    def any(self, *paths: str):
        return self.route(*paths, methods=None)

    def route(self, *paths: str, methods: Optional[Set[str]] = None):
        def decorator(target: t.Any = None):
            for path in paths:
                route = HttpRoute(
                    path=path,
                )

                for method in methods or (str(dict()),):
                    route.target.route(method)(target)

                self.routes.append(route)

            return target

        return decorator


class InverseRouter(mixins.InverseRouterMixin, Router):
    pass


class InverseHttpRouter(mixins.InverseRouterMixin, HttpRouter):
    pass
