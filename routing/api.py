import dataclasses
import inspect
from typing import Any, Dict, List

import annotate
import mediate

from . import models, enums
from .router import Router


def get_routes(obj: Any, /) -> List[models.Route]:
    if isinstance(obj, models.Route):
        return [obj]

    if isinstance(obj, Router):
        return obj.routes

    annotations: Dict[Any, annotate.Annotation] = annotate.get_annotations(obj)

    if enums.Annotation.ROUTE in annotations:
        return [
            dataclasses.replace(route, target=obj)
            for route in annotations[enums.Annotation.ROUTE]
        ]

    return [
        dataclasses.replace(route, target=member)
        for _, member in inspect.getmembers(obj)
        for route in annotate.get_annotations(member).get(enums.Annotation.ROUTE, ())
    ]


def get_middleware(obj: Any, /) -> List[Any]:
    if enums.Annotation.MIDDLEWARE in annotate.get_annotations(obj):
        return [obj]

    if isinstance(obj, Router):
        return obj.middlewares

    return [
        member
        for _, member in inspect.getmembers(obj)
        if enums.Annotation.MIDDLEWARE in annotate.get_annotations(member)
    ]


def router(*objs: Any) -> Router:
    middlewares: mediate.Middleware = mediate.Middleware()
    routes: List[models.Route] = []

    obj: Any
    for obj in objs:
        middleware: Any
        for middleware in get_middleware(obj):
            middlewares.append(middleware)

        route: models.Route
        for route in get_routes(obj):
            routes.append(route)

    return Router(routes=routes, middlewares=middlewares)
