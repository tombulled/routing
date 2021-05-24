import pydantic
import attr
import collections
import parse

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

class Path(collections.UserString):
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.data!r})'

    def __hash__(self) -> str:
        return hash(self.reduce())

    def __eq__(self, rhs: str) -> bool:
        return str.__eq__(self.reduce(), self.__class__.reduce(rhs))

    def reduce(self) -> str:
        parser = parse.compile(str(self))

        return self.format(** dict.fromkeys(parser.named_fields, str(dict())))

class AnyPath(Path):
    def __init__(self):
        super().__init__('*')

    def __repr__(self) -> str:
        return 'Path(*)'

    def __hash__(self) -> str:
        return hash(self.data)

    def __eq__(self, rhs: str) -> bool:
        return True

@attr.s(auto_attribs = True)
class BaseRoute(object):
    path:   Path = attr.ib(converter = lambda path: path if isinstance(path, Path) else Path(path))
    target: t.Any = None

@attr.s
class BaseRouter(object):
    routes: t.List[BaseRoute] = attr.ib(default=attr.Factory(list))

    def __call__(self, path: str):
        for route in self.routes:
            if route.path == path:
                return route.target if route.target is not None else route

        raise NotFound(path)

    def __getattr__(self, path: str):
        if path.startswith('_'):
            raise AttributeError

        return self.route(path)

    def route(self, *paths: str):
        def decorator(target: t.Any = None):
            for path in paths:
                if isinstance(target, self.__class__):
                    for route in target.routes:
                        self.routes.append \
                        (
                            BaseRoute \
                            (
                                path   = path + route.path,
                                target = route.target,
                            ),
                        )
                else:
                    self.routes.append \
                    (
                        BaseRoute \
                        (
                            path   = path,
                            target = target,
                        ),
                    )

            return target

        return decorator

class MethodRouter(BaseRouter):
    def __call__(self, path: str):
        try:
            return super().__call__(path)
        except NotFound:
            raise MethodNotAllowed(path) from None

@attr.s
class Route(BaseRoute):
    target: MethodRouter = attr.ib(default=attr.Factory(MethodRouter))

    def __call__(self, method: t.Optional[str] = None):
        return self.target(method)

    @property
    def any(self):
        return self.target.route(AnyPath())

    def __getattr__(self, method: str):
        return getattr(self.target, method)

class Router(BaseRouter):
    routes: t.List[Route] = attr.ib(default=attr.Factory(list))

    def __getattr__(self, method: str):
        if method.startswith('_'):
            raise AttributeError

        return functools.partial(self.route, methods={method})

    def any(self, *paths: str):
        return self.route(*paths, methods = {AnyPath()})

    def route(self, *paths: str, methods: Optional[Set[str]] = None):
        def decorator(target: t.Any = None):
            for path in paths:
                route = Route \
                (
                    path = path,
                )

                for method in methods or (AnyPath(),):
                    route.target.route(method)(target)

                self.routes.append(route)

            return target

        return decorator
