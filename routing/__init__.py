import dataclasses
import typing
import inspect
import itertools
import types

import furl
import parse

# import cassidy
# import sentinel
import mediate
import label

from . import errors
from . import sentinels
from . import models

# TODO: Make abstract base route class? (create protocol)
# TODO: Implement state? Just let them define custom Router classes instead?

Missing = object()

@dataclasses.dataclass
class Route:
    path:   str
    target: typing.Any = None # Make this only work for callables?

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.path!r})'

    def match(self, path) -> typing.Optional[dict]:
        result = parse.parse(self.path, path)

        return result and result.named

    def matches(self, path) -> bool:
        return self.match(path) is not None

class Middleware(mediate.Middleware):
    def __call__(self, func):
        return super().__call__(middleware(func))

@dataclasses.dataclass
class Router:
    routes: typing.List[Route] = dataclasses.field(default_factory = list)
    middleware: Middleware = dataclasses.field(default_factory = Middleware)

    def __call__(self, uri, *args, **kwargs):
        url = furl.furl(uri)
        path = str(url.path)
        query = dict(url.query.params)

        # context_hook = dict
        # params_hook = dict

        request = models.Request \
        (
            path    = path,
            router  = self,
            params  = models.Context(kwargs = query),
            context = models.Context(args, kwargs),
        )

        return self.handle(request)

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
        def proc(request):
            route = self.resolve(request.path)

            return route.target(*request.params.args, **request.params.kwargs)

        target = self.middleware.compose(proc)

        return target(request)

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
                target = Missing,
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
    routes = [Route(path, **kwargs) for path in paths]

    def decorator(func):
        labels = label.get_labels(func)

        labels.setdefault(sentinels.Route, [])

        labels[sentinels.Route] += routes

        return func

    return decorator

def mount(*paths: str):
    def decorator(func):
        mounts = \
        [
            * [models.Mount(path) for path in paths],
            * label.get_labels(func).get(sentinels.Mount, ())
        ]

        return label.label(sentinels.Mount, mounts)(func)

    return decorator

middleware = label.label(sentinels.Middleware)

def get_routes(obj, *, sep: str = ''): # TODO: Add 'depth' param? (e.g. whether to check attributes)
    labels = label.get_labels(obj)

    if sentinels.Route in labels:
        return \
        [
            Route \
            (
                path = \
                (
                    sep.join \
                    (
                        [
                            * [mount.path for mount in labels[sentinels.Mount]],
                            route.path,
                        ],
                    )
                    if sentinels.Mount in labels
                    else route.path
                ),
                target = obj,
            )
            for route in labels[sentinels.Route]
        ]

    return \
    [
        Route \
        (
            path = \
            (
                sep.join \
                (
                    [
                        * [mount.path for mount in labels[sentinels.Mount]],
                        route.path,
                    ],
                )
                if sentinels.Mount in label.get_labels(value)
                else route.path
            ),
            target = value,
        )
        for key, value in inspect.getmembers(obj)
        for route in label.get_labels(value).get(sentinels.Route, ())
    ]

def get_middleware(obj): # TODO: Add 'depth' param? (e.g. whether to check attributes)
    if sentinels.Middleware in label.get_labels(obj):
        return [obj]

    return \
    [
        value
        for key, value in inspect.getmembers(obj)
        if sentinels.Middleware in label.get_labels(value)
    ]

def router(*objs, sep: str = ''):
    middleware = Middleware()

    for obj in objs:
        for m in get_middleware(obj):
            middleware.append(m)

    return Router \
    (
        routes = \
        [
            route
            for obj in objs
            for route in ([obj] if isinstance(obj, Route) else get_routes(obj, sep=sep))
        ],
        middleware = middleware,
    )