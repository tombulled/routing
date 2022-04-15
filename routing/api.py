import dataclasses
import inspect
from typing import Any, Dict, List

import annotate
import mediate

from . import models, routers, sentinels


def get_routes(obj: Any, /) -> List[models.Route]:
    if isinstance(obj, models.Route):
        return [obj]

    if isinstance(obj, routers.Router):
        return obj.routes

    annotations: Dict[Any, annotate.Annotation] = annotate.get_annotations(obj)

    if sentinels.Route in annotations:
        return [
            dataclasses.replace(route, target=obj)
            for route in annotations[sentinels.Route]
        ]

    return [
        dataclasses.replace(route, target=member)
        for _, member in inspect.getmembers(obj)
        for route in annotate.get_annotations(member).get(sentinels.Route, ())
    ]


def get_middleware(obj: Any, /) -> List[Any]:
    if sentinels.Middleware in annotate.get_annotations(obj):
        return [obj]

    if isinstance(obj, routers.Router):
        return obj.middlewares

    return [
        member
        for _, member in inspect.getmembers(obj)
        if sentinels.Middleware in annotate.get_annotations(member)
    ]


def router(*objs: Any) -> routers.Router:
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

    return routers.Router(routes=routes, middlewares=middlewares)
