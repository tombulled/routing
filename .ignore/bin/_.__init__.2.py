import dataclasses
import typing
import inspect
import itertools

import furl
import parse

import mediate
import annotate

from . import errors
from . import sentinels
from . import models

# TODO: Make abstract base route class? (create protocol)
# TODO: Implement state? Just let them define custom Router classes instead?

Missing = object()


@dataclasses.dataclass
class Route:
    path: str
    target: typing.Any = None  # Make this only work for callables?

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.path!r})"

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
    routes: typing.List[Route] = dataclasses.field(default_factory=list)
    middleware: Middleware = dataclasses.field(default_factory=Middleware)

    def __call__(self, uri, *args, **kwargs):
        url = furl.furl(uri)
        path = str(url.path)
        query = dict(url.query.params)

        # context_hook = dict
        # params_hook = dict

        request = models.Request(
            path=path,
            router=self,
            params=models.Context(kwargs=query),
            context=models.Context(args, kwargs),
        )

        return self.handle(request)

    def __getitem__(self, path):
        return self.resolve(path)

    def __setitem__(self, path, target):
        self.routes.append(
            Route(
                path=path,
                target=target,
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
        new_routes = [
            Route(
                path=path,
                target=Missing,
            )
            for path in paths
        ]

        self.routes += new_routes

        def decorator(target):
            routes = annotate.get_annotations(target).get(sentinels.Route, ())

            annotate.annotate(
                target, sentinels.Route, list(itertools.chain(new_routes, routes))
            )

            for route in new_routes:
                route.target = target

            return target

        return decorator


def route(*paths: str, **kwargs):
    routes = [Route(path, **kwargs) for path in paths]

    def decorator(func):
        annotations = annotate.get_annotations(func)

        annotations.setdefault(sentinels.Route, [])

        annotations[sentinels.Route] += routes

        return func

    return decorator


def mount(*paths: str):
    def decorator(func):
        mounts = [
            *[models.Mount(path) for path in paths],
            *annotate.get_annotations(func).get(sentinels.Mount, ()),
        ]

        return annotate.Annotation(sentinels.Mount, mounts)(func)

    return decorator


middleware = annotate.Annotation(sentinels.Middleware)


def get_routes(
    obj, *, sep: str = ""
):  # TODO: Add 'depth' param? (e.g. whether to check attributes)
    annotations = annotate.get_annotations(obj)

    if sentinels.Route in annotations:
        return [
            Route(
                path=(
                    sep.join(
                        [
                            *[mount.path for mount in annotations[sentinels.Mount]],
                            route.path,
                        ],
                    )
                    if sentinels.Mount in annotations
                    else route.path
                ),
                target=obj,
            )
            for route in annotations[sentinels.Route]
        ]

    return [
        Route(
            path=(
                sep.join(
                    [
                        *[mount.path for mount in annotations[sentinels.Mount]],
                        route.path,
                    ],
                )
                if sentinels.Mount in annotate.get_annotations(value)
                else route.path
            ),
            target=value,
        )
        for key, value in inspect.getmembers(obj)
        for route in annotate.get_annotations(value).get(sentinels.Route, ())
    ]


def get_middleware(obj):  # TODO: Add 'depth' param? (e.g. whether to check attributes)
    if sentinels.Middleware in annotate.get_annotations(obj):
        return [obj]

    return [
        value
        for key, value in inspect.getmembers(obj)
        if sentinels.Middleware in annotate.get_annotations(value)
    ]


def router(*objs, sep: str = ""):
    middleware = Middleware()

    for obj in objs:
        for m in get_middleware(obj):
            middleware.append(m)

    return Router(
        routes=[
            route
            for obj in objs
            for route in ([obj] if isinstance(obj, Route) else get_routes(obj, sep=sep))
        ],
        middleware=middleware,
    )
