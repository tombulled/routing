import dataclasses
from typing import Any, List, TypeVar

from . import models
from . import errors
from . import sentinels
from . import annotations

import mediate
import arguments
import annotate


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
        route = self.resolve(request.path)

        args = route.match(request.path)

        request = dataclasses.replace(
            request,
            args=arguments.Arguments(*args, *request.args.args, **request.args.kwargs),
        )

        def process(request):
            return route.target(*request.args.args, **request.args.kwargs)

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
