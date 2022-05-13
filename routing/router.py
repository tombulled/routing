from abc import ABC, abstractmethod
import dataclasses
from typing import Any, Callable, Generic, List, Optional, TypeVar

from . import models
from . import errors
from . import enums
from . import annotations

import mediate
from arguments import Arguments
import annotate


T = TypeVar("T")
RO = TypeVar("RO", bound=models.AbstractRoute)
RE = TypeVar("RE", bound=models.AbstractRequest)


@dataclasses.dataclass
class AbstractRouter(Generic[RO, RE], ABC):
    routes: List[RO] = dataclasses.field(default_factory=list)
    middlewares: mediate.Middleware = dataclasses.field(
        default_factory=mediate.Middleware
    )
    separator: str = ""

    @staticmethod
    @abstractmethod
    def build_request(path: str, *args: Any, **kwargs: Any) -> RE:
        ...

    @staticmethod
    @abstractmethod
    def build_route(path: str, *args: Any, **kwargs: Any) -> RO:
        ...

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.handle(self.build_request(*args, **kwargs))

    def __getitem__(self, path: str, /) -> List[RO]:
        return [
            route
            for route in self.routes
            if route.matches(path)
        ]

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

    def route(self, *paths: str, **kwargs: Any) -> Callable[[Callable], Callable]:
        def wrapper(target: Callable, /) -> Callable:
            path: str
            for path in paths:
                route: RO = self.build_route(path, **kwargs, target=target)

                self.routes.append(dataclasses.replace(route))

                annotation: annotate.Annotation = annotate.Annotation(
                    key=enums.Annotation.ROUTE, value=route, repeatable=True
                )

                annotate.annotate(target, annotation)

            return target

        return wrapper

    def mount(self, *args, **kwargs) -> Callable[[T], T]:
        def wrapper(obj: T, /) -> T:
            mount: models.Mount = models.Mount(*args, **kwargs)

            routes: List[RO] = annotate.get_annotations(obj).get(
                enums.Annotation.ROUTE, []
            )

            route: RO
            for route in self.routes:
                if route in routes:
                    route.path = mount.apply(route.path, sep=self.separator)

            return obj

        return wrapper

    def middleware(self, obj: T) -> T:
        annotations.middleware(obj)

        self.middlewares.append(obj)

        return obj


@dataclasses.dataclass
class Router(AbstractRouter[models.Route, models.Request]):
    routes: List[models.Route] = dataclasses.field(default_factory=list)

    @staticmethod
    def build_request(path: str, *args: Any, **kwargs: Any) -> models.Request:
        return models.Request(path=path, data=Arguments(*args, **kwargs))

    @staticmethod
    def build_route(path: str, *args: Any, **kwargs: Any) -> models.Route:
        return models.Route(path, *args, **kwargs)

    def apply(self, route: RO, request: RE) -> Any:
        if route.target is None:
            return None

        args: Optional[Arguments] = route.match(request.path)

        if args is not None:
            request = dataclasses.replace(
                request,
                data=Arguments(*args, *request.data.args, **request.data.kwargs),
            )

        return route.target(*request.data.args, **request.data.kwargs)
