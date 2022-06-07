from abc import ABC
import dataclasses
from typing import Any, Callable, Generic, List, Optional, TypeVar

from . import models
from . import errors
from . import enums
from . import annotations

import mediate
from arguments import Arguments
import annotate


C = TypeVar("C", bound=Callable)
RO = TypeVar("RO", bound=models.AbstractRoute)
RE = TypeVar("RE", bound=models.AbstractRequest)


@dataclasses.dataclass
class AbstractRouter(Generic[RO, RE], ABC):
    routes: List[RO] = dataclasses.field(default_factory=list)
    middlewares: mediate.Middleware = dataclasses.field(
        default_factory=mediate.Middleware
    )
    separator: str = ""

    def build_route_registrar(self, routes: List[RO]) -> Callable[[C], C]:
        def wrapper(target: C, /) -> C:
            route: RO
            for route in routes:
                route = dataclasses.replace(route, target=target)

                self.routes.append(dataclasses.replace(route))

                annotation: annotate.Annotation = annotate.Annotation(
                    key=enums.Annotation.ROUTE, value=route, repeatable=True
                )

                annotate.annotate(target, annotation)

            return target

        return wrapper

    def build_mount_registrar(self, mount: models.Mount) -> Callable[[C], C]:
        def wrapper(obj: C, /) -> C:
            routes: List[RO] = annotate.get_annotations(obj).get(
                enums.Annotation.ROUTE, []
            )

            route: RO
            for route in self.routes:
                if route in routes:
                    route.path = mount.apply(route.path, sep=self.separator)

            return obj

        return wrapper

    def __getitem__(self, path: str, /) -> List[RO]:
        return [route for route in self.routes if route.matches(path)]

    def apply(self, route: RO, request: RE) -> Any:
        if route.target is None:
            return None

        return route.target(request.data)

    def compose(self, route: RO) -> Callable[[RE], Any]:
        def process(request: RE) -> Any:
            return self.apply(route, request)

        return self.middlewares.compose(process)

    def handle(self, request: RE) -> Any:
        route: RO = self.resolve(request.path)

        return self.compose(route)(request)

    def resolve(self, path: str) -> RO:
        routes: List[RO] = self[path]

        if not routes:
            raise errors.RouteNotFound(path)

        return routes[0]

    def mount(self, *args, **kwargs) -> Callable[[C], C]:
        mount: models.Mount = models.Mount(*args, **kwargs)

        return self.build_mount_registrar(mount)

    def middleware(self, obj: C) -> C:
        annotations.middleware(obj)

        self.middlewares.append(obj)

        return obj


@dataclasses.dataclass
class Router(AbstractRouter[models.Route, models.Request]):
    routes: List[models.Route] = dataclasses.field(default_factory=list)

    def __call__(self, path: str, *args: Any, **kwargs: Any) -> Any:
        return self.handle(models.Request(path, *args, **kwargs))

    def apply(self, route: models.Route, request: models.Request) -> Any:
        if route.target is None:
            return None

        args: Optional[Arguments] = route.match(request.path)

        if args is not None:
            request = dataclasses.replace(
                request,
                data=Arguments(*args, *request.data.args, **request.data.kwargs),
            )

        return route.target(*request.data.args, **request.data.kwargs)

    def route(self, path: str) -> Callable[[C], C]:
        route: models.Route = models.Route(path=path, target=None)

        return self.build_route_registrar([route])
