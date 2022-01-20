import dataclasses
import typing
import inspect
import itertools
import types

import case
import sentinel
import mediate

import label

from . import errors
from . import sentinels

# TODO: Make abstract base route class?
# TODO: Implement state? Just let them define custom Router classes instead?

# Paths can be anything (e.g. str, int, float)
# Targets can also be anything
# ^ This is fine, however decorators only work for functions/classes

@dataclasses.dataclass
class Context:
    args:   tuple
    kwargs: dict

@dataclasses.dataclass
class Request:
    path:   typing.Any
    context: Context

@dataclasses.dataclass
class Route:
    path:   typing.Any
    target: typing.Any = None

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.path!r})'

    def matches(self, path) -> bool:
        return self.path == path # Crude check for now

@dataclasses.dataclass
class Router:
    routes: typing.List[Route] = dataclasses.field(default_factory = list)
    middleware: mediate.Middleware = dataclasses.field(default_factory = mediate.Middleware)

    def __call__(self, path, *args, **kwargs):
        request = Request(path, Context(args, kwargs))

        self.handle(request)

    def __getitem__(self, path):
        return self.resolve(path)

    def __setitem__(self, path, target):
        self.routes.append \
        (
            Route \
            (
                path   = path,
                target = target,
            ),
        )

    def handle(self, request):
        route = self.resolve(request.path)

        return route.target(*request.context.args, **request.context.kwargs)

    def resolve(self, path):
        for route in self.routes:
            if route.matches(path):
                return route

        raise errors.NotFound

    def route(self, *paths: str, **kwargs):
        new_routes = \
        [
            Route \
            (
                path   = path,
                target = sentinel.Missing,
            )
            for path in paths
        ]

        self.routes += new_routes

        def decorator(target):
            routes = label.get_labels(target).get(sentinels.Route, ())

            label.apply_label(target, sentinels.Route, list(itertools.chain(new_routes, routes)))

            for route in new_routes:
                route.target = target

            return target

        return decorator

def route(*paths: str, **kwargs):
    def decorator(func):
        routes = \
        [
            * [Route(path, **kwargs) for path in paths],
            * label.get_labels(func).get(sentinels.Route, ())
        ]

        return label.label(sentinels.Route, routes)(func)

    return decorator

def get_routes(obj): # TODO: Add 'depth' param? (e.g. whether to check attributes)
    if sentinels.Route in label.get_labels(obj):
        return \
        [
            Route \
            (
                path   = route.path,
                target = obj,
            )
            for route in label.get_labels(obj)[sentinels.Route]
        ]

    return \
    [
        Route \
        (
            path   = route.path,
            target = value,
        )
        for key, value in inspect.getmembers(obj)
        for route in label.get_labels(value).get(sentinels.Route, ())
    ]

def router(*objs):
    return Router \
    (
        routes = \
        [
            route
            for obj in objs
            for route in ([obj] if isinstance(obj, Route) else get_routes(obj))
        ],
    )

# def route(*paths, **state):
#     frame = inspect.currentframe()
#
#     try:
#         in_class = '__qualname__' in frame.f_back.f_locals
#     finally:
#         del frame
#
#     if in_class:
#         r = Router()
#     else:
#         r = get_router()
#
#     return r.route(*paths, **state)

# def router(cls):
#     if not isinstance(cls, type):
#         raise Exception('@router only works with classes')
#
#     cls = dataclasses.dataclass(cls)
#
#     cls._router = Router \
#     (
#         routes = \
#         [
#             route
#             for value in cls.__dict__.values()
#             if hasattr(value, '_router')
#             for route in value._router.routes
#         ],
#     )
#
#     return cls

# def join(a, b):
#     return f'{a}{b}'

# def mount(path):
#     def wrapper(target):
#         if not hasattr(target, '_router'):
#             raise Exception('Cant mount non-routified target')
#
#         for route in target._router.routes:
#             route.path = join(path, route.path)
#
#         return target
#
#     return wrapper

# def middleware(func):
#     print('middleware:', func)
#
#     m = Middleware(handler = func)
#
#     func._middleware = m
#
#     print(m)
#
#     frame = inspect.currentframe()
#
#     try:
#         in_class = '__qualname__' in frame.f_back.f_locals
#     finally:
#         del frame
#
#     if in_class:
#         r = Router()
#     else:
#         r = get_router()
#
#     return r.middleware(func)

# root = Router()
#
# routers: typing.Dict[str, 'Router'] = dict \
# (
#     root = root,
# )
#
# def get_router(name = None):
#     if name is None or name == 'root':
#         return root
#
#     routers.setdefault(name, Router())
#
#     return routers[module]
