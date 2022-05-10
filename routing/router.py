import dataclasses
from typing import Any, Callable, Generic, List, TypeVar

from . import models
from . import errors
from . import enums
from . import annotations

import mediate
import arguments
import annotate


T = TypeVar("T")
R = TypeVar("R", bound=models.Route)


@dataclasses.dataclass
class AbstractRouter(Generic[R]):
    route_factory: Callable[..., R]
    routes: List[R] = dataclasses.field(default_factory=list)
    middlewares: mediate.Middleware = dataclasses.field(
        default_factory=mediate.Middleware
    )
    separator: str = ""

    def __call__(self, path: str, *args: Any, **kwargs: Any) -> Any:
        request: models.Request = models.Request(
            path=path,
            args=arguments.Arguments(*args, **kwargs),
        )

        return self.handle(request)

    def __getitem__(self, path: str, /) -> R:
        return self.resolve(path)

    def __setitem__(self, path: str, target: Callable) -> None:
        self.routes.append(
            self.route_factory(
                path=path,
                target=target,
            ),
        )

    def handle(self, request: models.Request) -> Any:
        route: R = self.resolve(request.path)

        args: arguments.Arguments = route.match(request.path)

        request = dataclasses.replace(
            request,
            args=arguments.Arguments(*args, *request.args.args, **request.args.kwargs),
        )

        def process(request: models.Request) -> Any:
            if route.target is None:
                return None

            return route.target(*request.args.args, **request.args.kwargs)

        target: Callable[[models.Request], Any] = self.middlewares.compose(process)

        return target(request)

    def resolve(self, path: str) -> R:
        route: R
        for route in self.routes:
            if route.matches(path):
                return route

        raise errors.RouteNotFound(repr(path))

    def route(self, *paths: str, **kwargs: Any) -> Callable[[Callable], Callable]:
        def wrapper(target: Callable, /) -> Callable:
            path: str
            for path in paths:
                route: R = self.route_factory(path, **kwargs, target=target)

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

            routes: List[R] = annotate.get_annotations(obj).get(
                enums.Annotation.ROUTE, []
            )

            route: R
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
class Router(AbstractRouter[models.Route]):
    route_factory: Callable[..., models.Route] = dataclasses.field(
        default=models.Route, init=False, repr=False
    )
    routes: List[models.Route] = dataclasses.field(default_factory=list)
