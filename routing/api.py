import dataclasses
import inspect
from typing import Any, List, TypeVar

import annotate
import arguments
import mediate

from . import annotations, errors, models, sentinels

T = TypeVar("T")


@dataclasses.dataclass
class Router:
    routes: List[models.Route] = dataclasses.field(default_factory=list)
    middlewares: mediate.Middleware = dataclasses.field(
        default_factory=mediate.Middleware
    )
    separator: str = ""

    def __call__(self, path, *args, **kwargs):
        request = models.Request(
            path=path,
            args=arguments.Arguments(*args, **kwargs),
        )

        return self.handle(request)

    def __getitem__(self, path):
        return self.resolve(path)

    def __setitem__(self, path, target):
        self.routes.append(
            models.Route(
                path=path,
                target=target,
            ),
        )

    def handle(self, request):
        def process(request):
            route = self.resolve(request.path)

            return route.target(*request.params.args, **request.params.kwargs)

        target = self.middlewares.compose(process)

        return target(request)

    def resolve(self, path):
        for route in self.routes:
            if route.matches(path):
                return route

        raise errors.RouteNotFound(repr(path))

    def route(self, *paths: str, **kwargs: Any):
        def wrapper(obj: T, /) -> T:
            for path in paths:
                route = models.Route(path, **kwargs, target=obj)

                self.routes.append(dataclasses.replace(route))

                annotation = annotate.Annotation(
                    key=sentinels.Route, value=route, repeatable=True
                )

                annotate.annotate(obj, annotation)

            return obj

        return wrapper

    def mount(self, *args, **kwargs):
        def wrapper(obj: T, /) -> T:
            mount: models.Mount = models.Mount(*args, **kwargs)

            routes = annotate.get_annotations(obj)[sentinels.Route]

            for route in self.routes:
                if route in routes:
                    route.path = self.separator.join(
                        (route.path, mount.path)
                        if mount.suffix
                        else (mount.path, route.path)
                    )

            return obj

        return wrapper

    def middleware(self, obj: T) -> T:
        annotations.middleware(obj)

        self.middlewares.append(obj)

        return obj


# TODO: Add 'depth' param? (e.g. whether to check attributes)
def get_routes(obj, *, sep: str = ""):
    annotations = annotate.get_annotations(obj)

    if sentinels.Route in annotations:
        return [
            dataclasses.replace(target=obj) for route in annotations[sentinels.Route]
        ]

    return [
        dataclasses.replace(route, target=member)
        for name, member in inspect.getmembers(obj)
        for route in annotate.get_annotations(member).get(sentinels.Route, ())
    ]


# TODO: Add 'depth' param? (e.g. whether to check attributes)
def get_middleware(obj):
    if sentinels.Middleware in annotate.get_annotations(obj):
        return [obj]

    return [
        member
        for name, member in inspect.getmembers(obj)
        if sentinels.Middleware in annotate.get_annotations(member)
    ]


def router(*objs, sep: str = ""):
    middlewares = mediate.Middleware()

    for obj in objs:
        for m in get_middleware(obj):
            middlewares.append(m)

    return Router(
        routes=[
            route
            for obj in objs
            for route in (
                [obj] if isinstance(obj, models.Route) else get_routes(obj, sep=sep)
            )
        ],
        middlewares=middlewares,
    )
